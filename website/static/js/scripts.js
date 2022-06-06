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
        // $("#selected_portfolio_id").val(value.id);
    });
}

// 取得 目前選擇群組 - id
function getPortfolio_id(){
    id = $("#stock-portfolios").val();
    $("#selected_portfolio_id_to_rename").val(id)
    $("#selected_portfolio_id_to_delete").val(id)
    console.log(id)
}
    
