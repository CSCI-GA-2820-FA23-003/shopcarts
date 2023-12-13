$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#shopcart_id").val(res.id);
        $("#customer_id").val(res.customer_id);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_id").val("");
        $("#shopcart_id").val("");
    }

    function clear_cartitem_form_data() {
        $("#product_id").val("");
        $("#cartitem_shopcart_id").val("");
        $("#price").val("");
        $("#quantity").val("");
    }

    // Updates the flash message area
    function flash_message(message, type) {
        $("#flash_message").empty();
        let alert = `<div class="alert alert-info" role="alert">${message}</div>`
        switch(type) {
            case 'success':
                alert = `<div class="alert alert-success" role="alert">${message}</div>`
                break;
            case 'info':
                alert = `<div class="alert alert-info" role="alert">${message}</div>`
                break;
            case 'warning':
                alert = `<div class="alert alert-warning" role="alert">${message}</div>`
                break;
            case 'danger':
                alert = `<div class="alert alert-danger" role="alert">${message}</div>`
                break;
            default:
        }
        $("#flash_message").append(alert);
    }

    // ****************************************
    // Create a Shopcart
    // ****************************************

    $("#create-btn").click(function () {

        let customer_id = $("#customer_id").val();

        let data = {
            customer_id,
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/api/shopcarts",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success", "success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger")
        });
    });


    // ****************************************
    // Update a Shopcart
    // ****************************************

    $("#update-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();
        let customer_id = $("#customer_id").val();

        let data = {
            customer_id
            // TODO: Add items field here to update
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/api/shopcarts/${shopcart_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success", "success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger")
        });

    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#retrieve-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/api/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: ''
        })

        // ajax.done(function(res){
        //     //alert(res.toSource())
        //     update_form_data(res)
        //     flash_message("Success", "success")
        // });

        ajax.done(function(res){
            update_form_data(res)
            let table = '<table class="table">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">ID</th>'
            table += '<th class="col-md-1">Customer ID</th>'
            table += '<th class="col-md-1">Items</th>'
            table += '</tr><tr>'
            table += '<th></th><th></th><th></th>'
            table += '<th class="col-md-1">Product ID</th>'
            table += '<th class="col-md-1">Price</th>'
            table += '<th class="col-md-1">Quantity</th>'
            table += '</tr></thead><tbody>'
    
            // Add the retrieved shopcart to the table
            table += `<tr><td id="shopcart-id-${res.id}">${res.id}</td><td id="customer-id-${res.customer_id}">${res.customer_id}</td><td>${res.items?.length || 0} items</td><td></td><td></td><td></td></tr>`;
            res.items.forEach(item => {
                table += `<tr><td></td><td></td><td></td><td id="product-id-${item.product_id}">${item.product_id}</td><td>$${item.price.toFixed(2)}</td><td>${item.quantity}</td></tr>`;
            });
            table += '</tbody></table>';
    
            // Display the table
            $("#search_results").empty().append(table);
            
            flash_message("Success", "success");
        });
        
        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message, "danger")
        });
        
    });

    // ****************************************
    // Delete a Shopcart
    // ****************************************

    $("#delete-btn").click(function () {

        let shopcart_id = $("#shopcart_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/shopcarts/${shopcart_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been Deleted!", "success")
        });

        ajax.fail(function(res){
            flash_message("Server error!", "danger")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        clear_form_data();
        $("#flash_message").empty();
    });

    // ****************************************
    // Search for a Shopcart
    // ****************************************

    $("#search-btn").click(function () {

        let customer_id = $("#customer_id").val();
        let shopcart_id = $("#shopcart_id").val();

        let queryString = "";
        let ajax;

        $("#flash_message").empty();
        // Use different route for query by shopcart_id and customer_id
        if (shopcart_id) {
            ajax = $.ajax({
                type: "GET",
                url: `/api/shopcarts/${shopcart_id}`,
                contentType: "application/json",
                data: ''
            })
        }
        else if (customer_id) {
            queryString += 'customer_id=' + customer_id;
            ajax = $.ajax({
                type: "GET",
                url: `/api/shopcarts?${queryString}`,
                contentType: "application/json",
                data: ''
            })
        }
        else{
            ajax = $.ajax({
                type: "GET",
                url: `/api/shopcarts?${queryString}`,
                contentType: "application/json",
                data: ''
            })
        }
        // Since query by customer_id returns a list and that query by shopcart-id returns one shopcart, it should be handled differently
        if(shopcart_id){
            ajax.done(function(res){
                update_form_data(res)
                let table = '<table class="table">'
                table += '<thead><tr>'
                table += '<th class="col-md-1">ID</th>'
                table += '<th class="col-md-1">Customer ID</th>'
                table += '<th class="col-md-1">Items</th>'
                table += '</tr><tr>'
                table += '<th></th><th></th><th></th>'
                table += '<th class="col-md-1">Product ID</th>'
                table += '<th class="col-md-1">Price</th>'
                table += '<th class="col-md-1">Quantity</th>'
                table += '</tr></thead><tbody>'
        
                // Add the retrieved shopcart to the table
                table += `<tr><td id="shopcart-id-${res.id}">${res.id}</td><td id="customer-id-${res.customer_id}">${res.customer_id}</td><td>${res.items?.length || 0} items</td><td></td><td></td><td></td></tr>`;
                res.items.forEach(item => {
                    table += `<tr><td></td><td></td><td></td><td id="product-id-${item.product_id}">${item.product_id}</td><td>$${item.price.toFixed(2)}</td><td>${item.quantity}</td></tr>`;
                });
                table += '</tbody></table>';
        
                // Display the table
                $("#search_results").empty().append(table);
                
                flash_message("Success", "success");
            });
        }
        else{
            ajax.done(function(res){
                //alert(res.toSource())
                console.log('here')
                $("#search_results").empty();
                let table = '<table class="table">'
                table += '<thead><tr>'
                table += '<th class="col-md-1">ID</th>'
                table += '<th class="col-md-1">Customer ID</th>'
                table += '<th class="col-md-1">Items</th>'
                table += '</tr><tr>'
                table += '<th></th><th></th><th></th>'
                table += '<th class="col-md-1">Product ID</th>'
                table += '<th class="col-md-1">Price</th>'
                table += '<th class="col-md-1">Quantity</th>'
                table += '</tr></thead><tbody>'
                let first_shopcart = "";
                for(let i = 0; i < res.length; i++) {
                    let shopcart = res[i];
                    table +=  `<tr id="row_${i}"><td id="shopcart-id-${shopcart.id}">${shopcart.id}</td><td id="customer-id-${shopcart.customer_id}">${shopcart.customer_id}</td><td>${shopcart.items?.length || 0} items</td><td></td><td></td><td></td></tr>`;
                    shopcart.items.forEach(item => {
                        table += `<tr><td></td><td></td><td></td><td id="product-id-${item.product_id}" class="active">${item.product_id}</td><td class="active">$${item.price.toFixed(2)}</td><td class="active">${item.quantity}</td></tr>`
                    })
                    if (i == 0) {
                        first_shopcart = shopcart;
                    }
                }
                table += '</tbody></table>';
                $("#search_results").append(table);
    
                // copy the first result to the form
                if (first_shopcart != "") {
                    update_form_data(first_shopcart)
                }
    
                flash_message("Success", "success")
            });
        }
        

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger")
        });

    });


    // ****************************************
    // Clear the CartItem form
    // ****************************************

    $("#cartitem-clear-btn").click(function () {
        $("#product_id").val("");
        $("#flash_message").empty();
        clear_cartitem_form_data();
    });

    // ****************************************
    // Create a CartItem in a Shopcart
    // ****************************************

    $("#cartitem-create-btn").click(function () {

        const shopcart_id = $("#cartitem_shopcart_id").val();
        const product_id = $("#product_id").val();
        const price = $("#price").val();
        const quantity = $("#quantity").val();

        const data = {
            price,
            product_id,
            quantity,
            shopcart_id
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: `/api/shopcarts/${shopcart_id}/items`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success", "success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message, "danger")
        });
    });

    // ****************************************
    // Update quantity, price, or both of a CartItem in a Shopcart
    // ****************************************
    $("#cartitem-update-btn").click(function () {
        const shopcart_id = $("#cartitem_shopcart_id").val();
        const product_id = $("#product_id").val();
        const new_quantity = $("#quantity").val();
        const new_price = $("#price").val();
    
        const data = {
            product_id,
            shopcart_id,
            new_quantity,
            new_price
        };
    
        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "PUT",
            url: `/api/shopcarts/${shopcart_id}/items/${product_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });
    
        ajax.done(function(res){
            clear_form_data();
            flash_message("Success", "success");
        });
    
        ajax.fail(function(res){
            flash_message("Server error!", "danger");
        });
    });

    // ****************************************
    // Delete a CartItem in a Shopcart
    // ****************************************

    $("#cartitem-delete-btn").click(function () {
        const shopcart_id = $("#cartitem_shopcart_id").val();
        const product_id = $("#product_id").val();

        const data = {
            product_id,
            shopcart_id
        };

        $("#flash_message").empty();
        let ajax = $.ajax({
            type: "DELETE",
            url: `/api/shopcarts/${shopcart_id}/items/${product_id}`,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            clear_form_data()
            flash_message("Success", "success")
        });

        ajax.fail(function(res){
            flash_message("Server error!", "danger")
        });
    });

    // ****************************************
    // Clear all items in the Shopcart
    // ****************************************
    $("#clearcart-btn").click(function () {
        let shopcart_id = $("#shopcart_id").val();
        console.log(shopcart_id);
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/api/shopcarts/${shopcart_id}/clear`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Shopcart has been cleared!", "success")
        });

        ajax.fail(function(res){
            flash_message("Server error!", "danger")
        });
    });
})
