import os
import cv2
import numpy as np


def _get_detection_files():
    dir_ = os.path.abspath(os.path.dirname(__file__))
    intel_dir = os.path.join(dir_, 'intel', 'text-detection-0004', 'FP16')

    bin_file = os.path.join(intel_dir, 'text-detection-0004.bin')
    xml_file = os.path.join(intel_dir, 'text-detection-0004.xml')

    return bin_file, xml_file


class PixelLinkDecoder():
    """ Decoder for Intel's version of PixelLink "text-detection-0003".
        You will need OpenCV compiled with Inference Engine to use this.
    """
    def __init__(self):
        bin, xml = _get_detection_files()
        self.td = cv2.dnn.readNet(xml, bin)

    def load(self, image, pixel_scores, link_scores,
             pixel_conf_threshold=None, link_conf_threshold=None, four_neighbours=False):
        self.image_shape = image.shape[0:2]
        self.pixel_scores = self._set_pixel_scores(pixel_scores)
        self.link_scores = self._set_link_scores(link_scores)

        if four_neighbours:
            self._get_neighbours = self._get_neighbours_4
        else:
            self._get_neighbours = self._get_neighbours_8

        if pixel_conf_threshold is None:
            self.pixel_conf_threshold = 0.75
        else:
            self.pixel_conf_threshold = pixel_conf_threshold

        if link_conf_threshold is None:
            self.link_conf_threshold = 0.9
        else:
            self.link_conf_threshold = link_conf_threshold

        self.pixel_mask = self.pixel_scores >= self.pixel_conf_threshold
        self.link_mask = self.link_scores >= self.link_conf_threshold
        self.points = list(zip(*np.where(self.pixel_mask)))
        self.h, self.w = np.shape(self.pixel_mask)
        self.group_mask = dict.fromkeys(self.points, -1)
        self.bboxes = None
        self.root_map = None
        self.mask = None

    def _softmax(self, x, axis=None):
        return np.exp(x - self._logsumexp(x, axis=axis, keepdims=True))

    def _logsumexp(self, a, axis=None, b=None, keepdims=False, return_sign=False):
        if b is not None:
            a, b = np.broadcast_arrays(a, b)
            if np.any(b == 0):
                a = a + 0.  # promote to at least float
                a[b == 0] = -np.inf

        a_max = np.amax(a, axis=axis, keepdims=True)

        if a_max.ndim > 0:
            a_max[~np.isfinite(a_max)] = 0
        elif not np.isfinite(a_max):
            a_max = 0

        if b is not None:
            b = np.asarray(b)
            tmp = b * np.exp(a - a_max)
        else:
            tmp = np.exp(a - a_max)

        # suppress warnings about log of zero
        with np.errstate(divide='ignore'):
            s = np.sum(tmp, axis=axis, keepdims=keepdims)
            if return_sign:
                sgn = np.sign(s)
                s *= sgn  # /= makes more sense but we need zero -> zero
            out = np.log(s)

        if not keepdims:
            a_max = np.squeeze(a_max, axis=axis)
        out += a_max

        if return_sign:
            return out, sgn
        else:
            return out

    def _set_pixel_scores(self, pixel_scores):
        "get softmaxed properly shaped pixel scores"
        tmp = np.transpose(pixel_scores, (0,2,3,1))
        return self._softmax(tmp, axis=-1)[0, :, :, 1]

    def _set_link_scores(self, link_scores):
        "get softmaxed properly shaped links scores"
        tmp = np.transpose(link_scores, (0,2,3,1))
        tmp_reshaped = tmp.reshape(tmp.shape[:-1]+(8, 2))
        return self._softmax(tmp_reshaped, axis=-1)[0, :, :, :, 1]

    def _find_root(self, point):
        root = point
        update_parent = False
        tmp = self.group_mask[root]
        while tmp is not -1:
            root = tmp
            tmp = self.group_mask[root]
            update_parent = True
        if update_parent:
            self.group_mask[point] = root
        return root

    def _join(self, p1, p2):
        root1 = self._find_root(p1)
        root2 = self._find_root(p2)
        if root1 != root2:
            self.group_mask[root2] = root1

    def _get_index(self, root):
        if root not in self.root_map:
            self.root_map[root] = len(self.root_map) + 1
        return self.root_map[root]

    def _get_all(self):
        self.root_map = {}
        self.mask = np.zeros_like(self.pixel_mask, dtype=np.int32)

        for point in self.points:
            point_root = self._find_root(point)
            bbox_idx = self._get_index(point_root)
            self.mask[point] = bbox_idx

    def _get_neighbours_8(self, x, y):
        w, h = self.w, self.h
        tmp = [(0, x - 1, y - 1), (1, x, y - 1),
               (2, x + 1, y - 1), (3, x - 1, y),
               (4, x + 1, y), (5, x - 1, y + 1),
               (6, x, y + 1), (7, x + 1, y + 1)]

        return [i for i in tmp if i[1] >= 0 and i[1] < w and i[2] >= 0 and i[2] < h]

    def _get_neighbours_4(self, x, y):
        w, h = self.w, self.h
        tmp = [(1, x, y - 1),
               (3, x - 1, y),
               (4, x + 1, y),
               (6, x, y + 1)]

        return [i for i in tmp if i[1] >= 0 and i[1] < w and i[2] >= 0 and i[2] < h]

    def _mask_to_bboxes(self, min_area=300, min_height=10):
        image_h, image_w = self.image_shape
        self.bboxes = []
        self.bbrect = []
        max_bbox_idx = self.mask.max()
        mask_tmp = cv2.resize(self.mask, (image_w, image_h), interpolation=cv2.INTER_NEAREST)

        for bbox_idx in range(1, max_bbox_idx + 1):
            bbox_mask = mask_tmp == bbox_idx
            cnts, _ = cv2.findContours(bbox_mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(cnts) == 0:
                continue
            cnt = cnts[0]
            rect, w, h, bb = self._min_area_rect(cnt)
            if min(w, h) < min_height:
                continue
            if w*h < min_area:
                continue
            self.bboxes.append(self._order_points(rect))
            self.bbrect.append(bb)


    def _min_area_rect(self, cnt):
        bb = cv2.boundingRect(cnt)
        rect = cv2.minAreaRect(cnt)
        w, h = rect[1]
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        return box, w, h, bb

    def _order_points(self, rect):
        """ (x, y)
            Order: TL, TR, BR, BL
        """
        tmp = np.zeros_like(rect)
        sums = rect.sum(axis = 1)
        tmp[0] = rect[np.argmin(sums)]
        tmp[2] = rect[np.argmax(sums)]
        diff = np.diff(rect, axis = 1)
        tmp[1] = rect[np.argmin(diff)]
        tmp[3] = rect[np.argmax(diff)]
        return tmp

    def decode(self):
        for point in self.points:
            y, x = point
            neighbours = self._get_neighbours(x, y)
            for n_idx, nx, ny in neighbours:
                link_value = self.link_mask[y, x, n_idx]
                pixel_cls = self.pixel_mask[ny, nx]
                if link_value and pixel_cls:
                    self._join(point, (ny, nx))

        self._get_all()
        self._mask_to_bboxes()

    def plot_result(self, image):
        img_tmp = image.copy()
        for rect in self.bboxes:
            cv2.drawContours(img_tmp, [rect], 0, (255,0,0), 2)
        return img_tmp

    def inference(self, img):
        blob = cv2.dnn.blobFromImage(img, 1, (1280,768))
        self.td.setInput(blob)
        a, b = self.td.forward(self.td.getUnconnectedOutLayersNames())
        self.load(img, b, a)
        self.decode()
        img_tmp = self.plot_result(img)
        return img_tmp, self.bbrect
