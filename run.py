import os
import sys
from LandsatFileInfo import LandsatFileInfo
import OrganizeDirectory as Od


if __name__ == "__main__":
    # Run Landsat 8 for forest monitoring
    # argv[1] = directory where targz files are stored.
    # argv[2] = directory where folder tree will be created to sabe processed
    # files.
    for subdir, dirs, files in os.walk(sys.argv[1]):
        for file in files:
            if file.endswith(".tar.gz"):
                print("Processing "+file)

                file_path = os.path.join(subdir, file)

                lc = LandsatFileInfo(file_path)
                # Ordering directory to receive results
                od = Od.OrganizeDirectory(root_dir_path=sys.argv[2],
                                          satellite_name=lc.get_satellite_name,
                                          satellite_index=''.join(lc.get_landsat_index()),       #NOQA
                                          year=str(lc.get_landsat_aquisition_date().year),      #NOQA
                                          month=str(lc.get_landsat_aquisition_date().month),    #NOQA
                                          file_name=lc.get_satellite_file_name)            #NOQA
                od.create_dir_satellite_index_year_month_file_name()
