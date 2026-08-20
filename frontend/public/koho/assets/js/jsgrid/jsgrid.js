(function($) {
    "use strict";
    $("#basicScenario").jsGrid({
        width: "100%",
        filtering: true,
        editing: true,
        inserting: true,
        sorting: true,
        paging: true,
        autoload: true,
        pageSize: 15,
        pageButtonCount: 5,
        deleteConfirm: "Do you really want to delete the client?",
        controller: db,
        fields: [
            { name: "Task", type: "text", width: 150 },
            { name: "Email", type: "text", width: 200 },
            { name: "Phone", type: "text", width: 150 },
            { name: "Assign", type: "text", width: 160 },
            { name: "Date", type: "text", width: 150 },
            { name: "Price", type: "text", width: 100 },
            { name: "Status", type: "html", width: 150 },
            { name: "Progress", type: "text", width: 100 },
            { type: "control" , width: 80 },
        ]
    });
    $("#sorting-table").jsGrid({
        height:"400px",
        width: "100%",
        autoload: true,
        selecting: false,
        controller: db,
        fields: [
            { name: "Id", type: "text", width: 50 },
            { name: "Product", type: "text", width: 150 },
            { name: "Order Id", type: "text", width: 100 },
            { name: "Price", type: "text", width: 100 },
            { name: "Quantity", type: "text", title: "Quantity", width: 90 },
            { name: "Shipped", type: "text", width: 150 },
            { name: "Total", type: "text", width: 100 },
        ]
    });
    $("#sort").click ( function() {
        var field = $("#sortingField").val();
        $("#sorting-table").jsGrid("sort", field);
    });
    $("#batchDelete").jsGrid({
        width: "100%",
        autoload: true,
        confirmDeleting: false,
        paging: true,
        controller: {
            loadData: function() {
                return db.clients;
            }
        },
        fields: [
            {
                headerTemplate: function() {
                    return $("<button>").attr("type", "button").text("Delete") .addClass("btn btn-danger btn-sm btn-delete mb-0")
                        .click( function () {
                            deleteSelectedItems();
                        });
            },
            itemTemplate: function(_, item) {
                return $("<input>").attr("type", "checkbox")
                        .prop("checked", $.inArray(item, selectedItems) > -1)
                        .on("change", function () {
                            $(this).is(":checked") ? selectItem(item) : unselectItem(item);
                        });
            },
            align: "center",
            width: 80
            },
            { name: "Id", type: "text", width: 50 },
            { name: "Employee Name", type: "Text", width: 150 },
            { name: "Salary", type: "text", width: 100 },
            { name: "Skill", type: "text", width: 60 },
            { name: "Office", type: "text", width: 100 },
            { name: "Hours", type: "text", width: 80 },
            { name: "Experience", type: "text", width: 110 },
        ]
    });
    var selectedItems = [];
    var selectItem = function(item) {
        selectedItems.push(item);
    };
    var unselectItem = function(item) {
        selectedItems = $.grep(selectedItems, function(i) {
            return i !== item;
        });
    };
    var deleteSelectedItems = function() {
        if(!selectedItems.length || !confirm("Are you sure?"))
            return;
        deleteClientsFromDb(selectedItems);
        var $grid = $("#batchDelete");
        $grid.jsGrid("option", "pageIndex", 1);
        $grid.jsGrid("loadData");
        selectedItems = [];
    };
    var deleteClientsFromDb = function(deletingClients) {
        db.clients = $.map(db.clients, function(client) {
            return ($.inArray(client, deletingClients) > -1) ? null : client;
        });
    };
})(jQuery);