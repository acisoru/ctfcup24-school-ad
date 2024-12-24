#!/bin/sh
# https://github.com/exaloop/codon

rm -rf build
rm -rf *.so
python3 setup.py build_ext --inplace
rm -rf build
mv session_authenticator.cpython*.so session_authenticator.so
echo "Testing"
python3 -c "import session_authenticator; print(session_authenticator.generate('a', 'bc'))"

# you need only session_authenticator.so file
