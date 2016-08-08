/**
 * Created by Oskar on 05.08.2016.
 */

angular
    .module('filterApp', ['ngMaterial'])
    .controller('ProductController', ['$scope', '$http', '$filter', '$log', function ($scope, $http, $filter, $log) {

        $scope.$log = $log;

        var products = [];

        var typeFilterList = [];

        // TODO add filter for providers
        var providerFilterList = [];

        var shownProducts = [];

        var updateProductList = function ($item) {

            var index = typeFilterList.indexOf($item);

            var p = new Object();
            var type = new Object();
            if (index >= 0) {
                console.log($item + " is in filter list");

                console.log(products);

                // if product has an attribute that is in typeFilterList then put into show

                for (var i = 0; i < products.length; i++) {
                    p = products[i];
                    type = p.product_type;
                    var type_index = typeFilterList.indexOf(type);
                    if (type_index > -1 && shownProducts.indexOf(p) == -1) {
                        console.log("type: " + type + " is in typefilterlist so product p: " + p.name + " is shown");
                        shownProducts.push(p);
                    }
                }
            } else {
                var j = shownProducts.length - 1;
                while(j >= 0) {
                    p = shownProducts[j];
                    type = p.product_type;
                    console.log("for loop: " + j + " type: " + type + " item: " + $item);
                    if (type === $item) {

                        console.log("time to splice");
                        shownProducts.splice(j, 1);

                    }

                    j--;
                }

                console.log($item + " is not in filter list anymore");
            }

            console.log(shownProducts.length);

            $scope.products = shownProducts;
        };

        $scope.modifyFilter = function ($scope, $filter, $item) {

            console.log("modifying item: " + $item + " to list");

            if (typeFilterList.indexOf($item) !== -1) {

                var index = typeFilterList.indexOf($item);
                if (index > -1) {
                    typeFilterList.splice(index, 1);
                }

                //$scope.typeFilterList = $filter('filter')($scope.typeFilterList, {name: '!' + item});

            } else {
                typeFilterList.push($item);
            }

            console.log("new list: " + typeFilterList + " " + $scope + " " + $item);

            updateProductList($item);
        };


        // GET Methods

        // categories
        $http({
            method: 'GET',
            url: '/api/v1/category/?format=json'
        }).then(function successCallback(response) {
            console.log("success calling categories");

            $scope.categories = response.data;

        }, function errorCallback(response) {
            console.log("error calling categories");
        });

        // product types
        $http({
            method: 'GET',
            url: '/api/v1/productType/?format=json'
        }).then(function successCallback(response) {
            console.log("success calling product types");

            $scope.productTypes = response.data;

        }, function errorCallback(response) {
            console.log("error calling product types");
        });

        // provider
        $http({
            method: 'GET',
            url: '/api/v1/provider/?format=json'
        }).then(function successCallback(response) {
            console.log("success calling provider");

            $scope.providers = response.data;

        }, function errorCallback(response) {
            console.log("error calling provider");
        });

        //products
        $http({
            method: 'GET',
            url: '/api/v1/product/?format=json'
        }).then(function successCallback(response) {

            console.log("success calling products");

            $scope.products = response.data;
            products = $scope.products;

        }, function errorCallback(response) {
            console.log("error on calling products");
        });


        // legacy

        $scope.sorts = [
            "Preis aufsteigend",
            "Preis absteigend",
            "Nach Hersteller",
            "Alphabetisch A-Z"
        ];

        $scope.selectedProducts = [];
    }]);
