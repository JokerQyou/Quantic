#!/bin/bash
# Quantic build tool
# This tool is used for building Quantic production version. 
# The source code of Quantic does not contain sensitive information 
# like database username and password, so you need to write those 
# information to build configuration files, and run this tool, 
# it will build out a Quantic ready for deployment. 
#
# @Author Joker Qyou 
# @Date 2014.09.27

set -o nounset
set -o errexit

current_dir=`dirname $0`

BUILD_TOOL_VERSION="0.1.1"
BUILD_SCRIPT_DIR="${current_dir}/build.script"

INFO_ABOUT="Quantic build tool ${BUILD_TOOL_VERSION} "
ERROR_NO_SCRIPT_DIR="\`build.config\` directory does not exist! "
ERROR_NO_SCRIPT_FOUND="No build script found! "

echo "${INFO_ABOUT}"

if [ ! -x ${BUILD_SCRIPT_DIR} ]; then
    echo ${ERROR_NO_SCRIPT_DIR}
else
    if [ `find ${BUILD_SCRIPT_DIR} -type f | wc -l` -le 0 ]; then
        echo ${ERROR_NO_SCRIPT_FOUND}
    else
        echo "Current dir: ${current_dir}"
        for build_script in `ls ${BUILD_SCRIPT_DIR}`; do
            echo "${build_script}"
        done
    fi
fi

