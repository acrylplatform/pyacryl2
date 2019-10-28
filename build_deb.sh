#while read package; do
#  fpm --python-bin python3 --python-pip pip3 --python-package-name-prefix "python36" -s python -t deb "$package"
#done <requirements.txt
#fpm --python-bin python3 --python-pip pip3 --python-package-name-prefix "python36" --python-obey-requirements-txt -s python -t deb ./setup.py && mv *.deb /result/
NAME=pyacryl2
VERSION=0.1.4

python3 setup.py bdist_wheel
WHEEL=$(ls dist/"${NAME}-${VERSION}"*.whl)
echo "Found wheel: ${WHEEL}"
pip3 install virtualenv virtualenv-tools3
fpm -s virtualenv -t deb --python-bin python3 --name $NAME -v $VERSION --virtualenv-setup-install --prefix /opt/pyacryl2/virtualenv $WHEEL && mv *.deb /result/
