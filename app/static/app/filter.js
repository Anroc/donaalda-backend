/**
 * Created by Oskar on 05.08.2016.
 */

angular
    .module('filterApp', ['ngMaterial'])
    .controller('ProductController', ['$scope', '$http', '$log', function ($scope, $http, $log) {

        $scope.$log = $log;

        $scope.sorts = [
            "Preis aufsteigend",
            "Preis absteigend",
            "Nach Hersteller",
            "Alphabetisch A-Z"
        ];

        $scope.selectedProducts = [];

        $scope.toggle = function (item, list) {
            var idx = list.indexOf(item);
            if (idx > -1) {
                list.splice(idx, 1);
            }
            else {
                list.push(item);
            }
        };

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

        }, function errorCallback(response) {
            console.log("error on calling products");
        });
    }]);
