/* Javascript for QnetXBlock. */
function QnetXBlock(runtime, element) {

    !function() {

        // save used elements
        var $result = $('[data-action="result"]', element),
            $error = $('[data-action="error"]', element),
            $controls = $('button', element);


        // get current lab status
        getData(runtime.handlerUrl(element, 'get_qnet_status'))
            .done(function(response) {
                // check indices
                if (!response.limited || response.vacant) {
                    $controls.prop('disabled', false);
                }
                else {
                    $error.removeClass('-hidden').text('нет свободных вариантов');
                }
            })
            .fail(function() {
                $error.removeClass('-hidden').text('не удалось получить сведения о работе');
            });

        // Event: click on submit button
        $('[data-action="submit"]', element).click(function(e) {
            window.location = runtime.handlerUrl(element, 'start_qnet_lab');
        });

        // Event: click on progress button
        $('[data-action="progress"]', element).click(function(e) {
            $error.addClass('-hidden').text('');
            $controls.prop('disabled', true);
            // get user progress
            getData(runtime.handlerUrl(element, 'get_qnet_progress'))
                .done(function(response) {
                    $result.html(getProgressText(response));
                    $controls.prop('disabled', false);
                })
                .fail(function() {
                    $error.removeClass('-hidden').text('не удалось получить результаты пользователя');
                    $controls.prop('disabled', false);
                });
        });

    }();


    // helper for get method
    function getData(url) {
        return $.ajax(url, {
            method: 'GET',
            dataType: 'json',
            timeout: 5000,
            cache: false
        });
    }

    // convert progress response to inserted text
    function getProgressText(response) {
        return 'Статус: ' + (response.is_done ? 'выполнено' : 'не выполнено') + ' (' +
            Number(response.score).toFixed(1) + '/' + Number(response.max_score).toFixed(1) + ' баллов)';
    }

}
