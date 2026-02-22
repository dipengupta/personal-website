(function () {
    var STORAGE_KEY = 'dipen-site-theme';
    var THEMES = ['light', 'dark', 'beige', 'chaos'];

    function normalizeTheme(theme) {
        return THEMES.indexOf(theme) >= 0 ? theme : 'light';
    }

    function getCurrentTheme() {
        return normalizeTheme(document.documentElement.getAttribute('data-theme'));
    }

    function setTheme(theme) {
        var nextTheme = normalizeTheme(theme);
        document.documentElement.setAttribute('data-theme', nextTheme);
        try {
            localStorage.setItem(STORAGE_KEY, nextTheme);
        } catch (e) {
            // Ignore storage errors (private mode / disabled storage).
        }
        syncThemeControls(nextTheme);
    }

    function syncThemeControls(theme) {
        var normalized = normalizeTheme(theme);
        var radios = document.querySelectorAll('input[name="site-theme"]');
        var track = document.querySelector('[data-theme-track]');
        var index = THEMES.indexOf(normalized);
        var activeLabel = null;

        radios.forEach(function (radio) {
            var isActive = radio.value === normalized;
            radio.checked = isActive;
            if (isActive && radio.nextElementSibling) {
                activeLabel = radio.nextElementSibling;
            }
        });

        if (track && index >= 0) {
            track.style.setProperty('--theme-index', String(index));
            track.setAttribute('data-index', String(index));
            if (activeLabel) {
                track.style.setProperty('--theme-thumb-left', activeLabel.offsetLeft + 'px');
                track.style.setProperty('--theme-thumb-width', activeLabel.offsetWidth + 'px');
            }
        }
    }

    function initTheme() {
        var savedTheme;
        try {
            savedTheme = localStorage.getItem(STORAGE_KEY);
        } catch (e) {
            savedTheme = null;
        }

        setTheme(savedTheme || getCurrentTheme());
    }

    function bindThemeControls() {
        var radios = document.querySelectorAll('input[name="site-theme"]');
        if (!radios.length) {
            return;
        }

        radios.forEach(function (radio) {
            radio.addEventListener('change', function (event) {
                if (event.target.checked) {
                    setTheme(event.target.value);
                }
            });
        });

        syncThemeControls(getCurrentTheme());
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            initTheme();
            bindThemeControls();
        });
    } else {
        initTheme();
        bindThemeControls();
    }

    window.addEventListener('storage', function (event) {
        if (event.key === STORAGE_KEY && event.newValue) {
            setTheme(event.newValue);
        }
    });

    window.addEventListener('resize', function () {
        syncThemeControls(getCurrentTheme());
    });
})();
