/* Javascript for QnetXBlock Edit */
function QnetXBlockEdit(runtime, element) {

    // Save xblock data
    function save_data() {
        var data = {};
        $('.input', element).each(function(index, input) {
            data[input.name] = input.value;
        });

        runtime.notify('save', { state: 'start' });
        var handlerUrl = runtime.handlerUrl(element, 'save_data');

        $.post(handlerUrl, JSON.stringify(data)).done(function(response) {
            runtime.notify('save', { state: 'end' });
        }).fail(function(jqXHR, textStatus, errorThrown) {
            runtime.notify('error', { msg: textStatus });
        });
    }

    return {
        save: save_data
    }

}
