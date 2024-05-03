#!/bin/bash
# additional_pkgs.bash への変更をdockerイメージに反映するために実行するスクリプト

set -e

./stop.sh

export VER=`date "+%Y%m%d_%H%M%S"`

source scripts/docker_util.sh
$docker_compose --profile runtime_base up --no-start # buildじゃなくてupなのは、一旦pull出来ないか確認するため
$docker_compose --profile runtime_base down # buildじゃないのでコンテナ出来ちゃうから、終わったら落としておく

$docker_compose --profile runtime build

echo VER=$VER > docker/ver.env
