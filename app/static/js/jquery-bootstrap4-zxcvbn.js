// requires Bootstrap 4 / zxcvbn
(function ($) {
    var settings;
    $.fn.zxcvbnProgress = function (options) {
        settings = $.extend({
            ratings: ["Very weak", "weak", "OK", "Strong", "Very strong"],
            progressClasses: ['bg-danger', 'bg-warning', 'bg-warning', 'bg-success', 'bg-success']
        }, options);
        
        var $passwordInputText = $(settings.passwordInputText);
        var $passwordInput = $(settings.passwordInput),$progress = this;
        $passwordInput.on('keyup', function () {
            updateProgress($passwordInput, $progress);
        });
        updateProgress($passwordInput, $progress, $passwordInputText);
    };
    function updateProgress($passwordInput, $progress, $passwordInputText) {
        var passwordValue = $passwordInput.val();
        if (passwordValue) {
            var result = zxcvbn(passwordValue, settings.userInputs),
                score = result.score,
                scorePercentage = (score + 1) * 20;
            $progress.css('width', scorePercentage + '%');
            $progress.removeClass(settings.progressClasses.join(' ')).addClass(settings.progressClasses[score]);
            $passwordInputText.text(settings.ratings[score]);
        } else {
            $progress.css('width', 0 + '%');
            $progress.removeClass(settings.progressClasses.join(' '))
            $passwordInputText.text('');
        }
    }
})(jQuery);
