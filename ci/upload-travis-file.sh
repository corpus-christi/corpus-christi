#!/bin/bash

echo We are about to push!
git add .travis.yml
git commit --fixup 09eaa46
git push
echo we have pushed!!
