def main():
    if args.model_path.endswith('.xml'):
        td = cv2.dnn.readNet(args.model_path, args.model_path[:-3] + 'bin')
    else:
        print("Model's XML file expected")
        return 1

    img = cv2.imread(args.image_path)
    if img is None:
        print("Failed to load image")
        return 1

    out_layer_names = td.getUnconnectedOutLayersNames()
    expected_out_layer_names = (['model/link_logits_/add', 'model/segm_logits/add'],
                                ['pixel_cls/add_2', 'pixel_link/add_2'])
    if out_layer_names not in expected_out_layer_names:
        print("Net has unexpected output layer names, please check model files")
        print("Expected: '{e}', returned: '{r}'".format(e=expected_out_layer_names, r=out_layer_names))
        return 1

    blob = cv2.dnn.blobFromImage(img, 1, (1280, 768))
    td.setInput(blob)
    a, b = td.forward(out_layer_names)

    expected_a_shape = (1, 16, 192, 320)
    expected_b_shape = (1, 2, 192, 320)
    if a.shape != expected_a_shape or b.shape != expected_b_shape:
This conversation was marked as resolved by Wovchena
        print("Net has returned outputs of different shape, please check model files")
        print("Expected shapes: ({ea}, {eb}), returned: ({ra}, {rb})".format(ea=expected_a_shape,
                                                                             eb=expected_b_shape,
                                                                             ra=a.shape, rb=b.shape))
        return 1

    dcd = PixelLinkDecoder()
    dcd.load(img, a, b)
    dcd.decode()  # results are in dcd.bboxes
    dcd.plot_result_cvgui(img)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", required=True, dest="image_path", help="path to input image")
    ap.add_argument("-m", required=True, dest="model_path", help="path to model's XML file")
    ap.add_argument("--no_show", dest="test", action='store_true', help="disable imshow() and wwaitKey()")
    ap.set_defaults(test=False)
    args = ap.parse_args()

