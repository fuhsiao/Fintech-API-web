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