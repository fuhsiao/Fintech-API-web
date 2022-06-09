/*!
    * Start Bootstrap - SB Admin v7.0.5 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2022 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});

// 設置 投資取向-下拉式選項
function setOptions(options){
    $.each(options,function(index,value){
        switch (value.category){
            case 'op1':
                $("#select-op1").append(new Option(value.name,value.id));
                break;
            case 'op2':
                $("#select-op2").append(new Option(value.name,value.id));
                break;
            case 'op3':
                $("#select-op3").append(new Option(value.name,value.id));
                break;
        }
    })
}

// 設置 投資組合-選擇群組 下拉選項
function setPortfolio_options(options){
    $.each(options,function(index,value){
        $("#stock-portfolios").append(new Option(value.name,value.id));
    });
}

// 取得 目前選擇群組 - id
function setPortfolio_id(){
    id = $("#stock-portfolios").val();
    index = $("#stock-portfolios").prop('selectedIndex')
    $("#rename_portfolio_index").val(index)
    $("#addstock_portfolio_index").val(index)
    $("#selected_portfolio_id_to_rename").val(id)
    $("#selected_portfolio_id_to_delete").val(id)
    $("#selected_portfolio_id_to_addStock").val(id)
}

// post like form
function url_redirect(options){
    var $form = $("<form />");
    
    $form.attr("action",options.url);
    $form.attr("method",options.method);
    
    for (var data in options.data)
    $form.append('<input type="hidden" name="'+data+'" value="'+options.data[data]+'" />');
    
    $("body").append($form);
    $form.submit();
}

// 切換群組 - 重整頁面至對應資料表格
function getData_by_change_select(){
    $('#stock-portfolios').on('change', function() {
        id = $("#stock-portfolios").val();
        selectedIndex = $("#stock-portfolios").prop('selectedIndex')
        console.log(selectedIndex)
        debugger
        url_redirect({url:'/portfolio_index_router', method: "post",data: {"index":selectedIndex}});
      });
}

// 刪除 股票
function delete_stock(stock_id){
    selectedIndex = $("#stock-portfolios").prop('selectedIndex')
    portfolio_id = $("#stock-portfolios").val();
    url_redirect({url:'/delete_stock', method: "post", data: {"stock_id":stock_id,"portfolio_id":portfolio_id, "index":selectedIndex}})
}

// 刪除 投資計畫
 function delete_plan (plan_id) {
    url_redirect({url:'/delete_plan', method: "post", data: {"plan_id":plan_id}})
}

// 判斷是否顯示 刪除投資組合選項
function judge_delete_portfolio_disable(){
    if($("#stock-portfolios>option").length < 2){
        $("#delete_portfolio_btn").addClass('disabled d-none')
    }
}

// 投資組合 初始設置函數
function init_portfolio(user_portfolios,portfolio_index){
    setPortfolio_options(user_portfolios) // 選擇群組-下拉選項
    getData_by_change_select() // 切換群組 重整至對應表格
    $("#stock-portfolios").prop("selectedIndex",portfolio_index);// 設置選擇群組
    setPortfolio_id() // 設置目前選擇群組 ID 到控制項
    judge_delete_portfolio_disable() // 是否顯示 刪除組合選項
}