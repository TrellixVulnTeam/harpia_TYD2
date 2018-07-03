import os


class ComposeBands:

    def __init__(self, input_dir, output_dir, output_file_name):
        """Init.

        Argument:
            input_dir [str] -- The path where all images are.
            output_dir [str] -- The path where compose image will be saved.
            output_file_name [str] -- Name of file without extension.
        """
        self.input_dir = input_dir

        self.output_dir = output_dir

        self.output_file_name = output_file_name

    def stack_img(self, expression):
        """Stacking bands from landsat in tmp folder.

        Argument:
            expression {str} -- Regular expression which select files who will be put in output.
        """

        # Path where band files can be find.
        # Here, it is the input for gdal_merge.
        input_img_dir = os.path.join(self.input_dir, expression)

        # Output image
        output_image_path = os.path.join(self.output_dir, self.output_file_name)

        command = "gdal_merge.py -separate -of HFA -co COMPRESSED=YES -o {output_image_path} " \
                  "{input_img_dir}".format(output_image_path=output_image_path,
                                           input_img_dir=input_img_dir)
        os.system(command)

    # def run_image_composition(self):

    #     # Stacking image to cloud/shadow
    #     self.stack_img(output_image_path=self.dir_tmp_img,
    #                    output_image_name="ref.img",
    #                    expression="LC08*_B[1-7,9].TIF")
    #     self.stack_img(self.dir_tmp_img, "thermal.img", "LC08*_B1[0,1].TIF")

    #     # Stacking imagem to clip
    #     self.stack_img(self.dir_tmp_img, self.file_name + ".TIF", expression="LC08*_B[3-6].TIF")

