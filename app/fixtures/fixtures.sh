#!/bin/sh

config="--format=json --indent=4 --exclude=app.employee"
no_dependency="--exclude=app.category --exclude=app.producttype --exclude=app.provider --exclude=app.provider --exclude=app.tag --exclude=app.question"
ex_auth="--exclude=auth"
stage_two="--exclude=app.product --exclude=app.providerprofile --exclude=app.answer"
product_set="--exclude=app.productset"
scenario="--exclude=app.scenario"
last="--exclude=app.scenariodescription --exclude=app.comment --exclude=app.userimage"

python3 ../../manage.py dumpdata $config $ex_auth $stage_two $product_set $scenario $last app auth > 001_no_dep.json
echo "Category, ProductType, Provider dumped"
python3 ../../manage.py dumpdata $config $no_dependency $stage_two $product_set $scenario $last app auth > 002_auth.json
echo "auth dumped"
python3 ../../manage.py dumpdata $config $no_dependency $ex_auth $product_set $scenario $last app auth > 003_staging.json
echo "Product, ProviderProfile dumped"
python3 ../../manage.py dumpdata $config $no_dependency $ex_auth $stage_two $scenario $last app auth > 004_prod.json
echo "ProductSet dumped"
python3 ../../manage.py dumpdata $config $no_dependency $ex_auth $stage_two $product_set $last app auth > 005_scenario.json
echo "Scenario dumped"
python3 ../../manage.py dumpdata $config $no_dependency $ex_auth $stage_two $product_set $scenario app auth > 006_last.json
echo "ScenarioDescription, Comment, UserImage dumped"
echo "all finished"
