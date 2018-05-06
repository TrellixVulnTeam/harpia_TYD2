Welcome to the preprocess2ta wiki!

# Instalar gdal

sudo add-apt-repository -y ppa:ubuntugis/ppa

sudo apt update

sudo apt upgrade

sudo apt install gdal-bin python-gdal python3-gdal

# Instalar OpenCV
sudo apt-get install gcc g++ git cmake

git clone https://github.com/opencv/opencv.git
git checkout 3.4.1

git clone https://github.com/opencv/opencv_contrib.git
git checkout 3.4.1

cd opencv
mkdir build
cd build
cmake CMAKE_VERBOSE=1 -DOPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules -DCMAKE_SKIP_RPATH=ON ../
make -j4
sudo make install

# Instalar o gdal-segment

cd gdal-segment
mkdir build
cd build
cmake -DCMAKE_CXX_FLAGS="-std=c++11 -fopenmp" ../
sudo make
