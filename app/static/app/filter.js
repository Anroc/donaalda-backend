/**
 * Created by Oskar on 05.08.2016.
 */

angular
    .module('filterApp', ['ngMaterial', 'directives.rangeSlider'])
    .controller('sorting', function ($scope) {
        $scope.sorts = [
            "Preis aufsteigend",
            "Preis absteigend",
            "Nach Hersteller",
            "Alphabetisch A-Z"
        ];
    })
    .controller('AppCtrl', function ($scope) {
    })
    .controller('AppCtrl2', function ($scope, $http) {

        console.log("angular test");
        $http({
            method: 'GET',
            url: '/api/v1/product/?format=json'
        }).then(function successCallback(response) {
            // this callback will be called asynchronously
            // when the response is available

            console.log("success");
            console.log(response);

            console.log("data:");
            console.log(response.data);

            var products = response.data;

            console.log("Products is instance of: ");
            for(var i = 0; i <= products.length; i++) {

                var product = products[i];

                console.log(product);

                var provider = product.provider.name;
                console.log("name: " + product.name + ", provider: " + provider);
            }

        }, function errorCallback(response) {
            // called asynchronously if an error occurs
            // or server returns response with an error status.
        });
    });

//directive for range-slider
angular.module('directives.rangeSlider', ['ngMaterial'])
    .directive('rangeSlider', function () {
        return {
            restrict: "E",
            scope: {
                max: '=',
                min: '=',
                gap: '=?',
                step: '=?',
                lowerValue: "=",
                upperValue: "="
            },
            templateUrl: 'range-slider.tpl.html',
            controller: ["$scope", function ($scope) {

                var COMFORTABLE_STEP = $scope.step, // whether the step is comfortable that depends on u
                    tracker = $scope.tracker = {    // track style
                        width: 0,
                        left: 0,
                        right: 0
                    };

                function updateSliders() {

                    if ($scope.upperValue - $scope.lowerValue > $scope.gap) {

                        $scope.lowerMaxLimit = $scope.lowerValue + COMFORTABLE_STEP;
                        $scope.upperMinLimit = $scope.upperValue - COMFORTABLE_STEP;

                    } else {
                        $scope.lowerMaxLimit = $scope.lowerValue;
                        $scope.upperMinLimit = $scope.upperValue;
                    }

                    updateSlidersStyle();

                }

                function updateSlidersStyle() {
                    // update sliders style
                    $scope.lowerWidth = $scope.lowerMaxLimit / $scope.max * 100;
                    $scope.upperWidth = ($scope.max - $scope.upperMinLimit) / $scope.max * 100;

                    // update tracker line style
                    tracker.width = 100 - $scope.lowerWidth - $scope.upperWidth;
                    tracker.left = $scope.lowerWidth || 0;
                    tracker.right = $scope.upperWidth || 0;
                }

                // watch lowerValue & upperValue to update sliders
                $scope.$watchGroup(["lowerValue", "upperValue"], function (newVal) {

                    // filter the default initialization
                    if (newVal !== undefined) {
                        updateSliders();
                    }

                });

                // init
                $scope.step = $scope.step || 1;
                $scope.gap = $scope.gap || 0;
                $scope.lowerMaxLimit = $scope.lowerValue + COMFORTABLE_STEP;
                $scope.upperMinLimit = $scope.upperValue - COMFORTABLE_STEP;
                updateSlidersStyle();
            }]
        };

    });