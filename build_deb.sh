while read package; do
  fpm --python-bin python3 --python-pip pip3 --python-package-name-prefix "python3" -s python -t deb "$package"
done <requirements.txt
fpm --python-bin python3 --python-pip pip3 --python-package-name-prefix "python3" --python-obey-requirements-txt -s python -t deb ./setup.py && mv *.deb /result/
