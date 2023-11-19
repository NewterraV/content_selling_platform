$(function ($) {
    $('#ajax_subscribe').submit(function (e) {
        e.preventDefault()
        console.log(this)
        let btn = $(this).find('#subs');
        $.ajax({
            type: this.method,
            url: this.action,
            data: $(this).serialize(),
            success: function (response) {
                btn.val('Отписаться');
            },
            error: function (response) {
                btn.val('Подписаться бесплатно');
            }
        })
    })
})