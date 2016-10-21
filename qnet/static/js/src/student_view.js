/* Javascript for QnetXBlock. */
function QnetXBlock(runtime, element) {

    !function() {

        // save used elements
        var $outResult = $('[data-out="result"]', element),
            $outError = $('[data-out="error"]', element),
            $btnSubmit = $('[data-action="submit"]', element),
            $btnProgress = $('[data-action="progress"]', element),
            $controls = $('button', element),
            isReady = false;

        // get current lab status
        getData(runtime.handlerUrl(element, 'get_qnet_status'))
            .done(function(response) {
                // check indices
                if (!response.limited || response.vacant) {
                    isReady = true;
                    $btnSubmit.prop('disabled', false);
                }
                else {
                    $outError.removeClass('-hidden').text('нет свободных вариантов');
                }
                $btnProgress.prop('disabled', false);
            })
            .fail(function() {
                $outError.removeClass('-hidden').text('не удалось получить сведения о работе');
            });

        // Event: click on submit button
        $btnSubmit.click(function(e) {
            // disable buttons before redirect
            $controls.prop('disabled', false);

            var location = runtime.handlerUrl(element, 'start_qnet_lab');
            console.log('goto: ', location);

            window.location = location;
        });

        // Event: click on progress button
        $btnProgress.click(function(e) {
            $outError.addClass('-hidden').text('');
            $controls.prop('disabled', true);
            // get user progress
            getData(runtime.handlerUrl(element, 'get_qnet_progress'))
                .done(function(response) {
                    $outResult.html(getProgressText(response));
                })
                .fail(function() {
                    $outError.removeClass('-hidden').text('не удалось получить результаты пользователя');
                })
                .always(function() {
                    $btnProgress.prop('disabled', false);
                    $btnSubmit.prop('disabled', !isReady);
                });
        });

    }();


    // helper for get method
    function getData(url) {
        return $.ajax(url, {
            method: 'GET',
            dataType: 'json',
            timeout: 30000,
            cache: false
        });
    }

    // convert progress response to inserted text
    function getProgressText(response) {
        return 'Статус: ' + (response.is_done ? 'выполнено' : 'не выполнено') + ' (' +
            Number(response.score).toFixed(1) + '/' + Number(response.max_score).toFixed(1) + ' баллов)';
    }

}
