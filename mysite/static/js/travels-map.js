(function () {
    var dataNode = document.getElementById("travel-points-data");
    var mapNode = document.getElementById("travels-map");
    if (!dataNode || !mapNode || typeof L === "undefined") {
        return;
    }

    var points = [];
    try {
        points = JSON.parse(dataNode.textContent || "[]");
    } catch (err) {
        console.error("Failed to parse travel points", err);
        return;
    }

    var colors = {
        visited: "#007f87",
        mug: "#c75b12"
    };

    var defaultView = {
        center: [40.85, -77.8], // Start near PA as requested; users can pan/zoom out.
        zoom: 5
    };

    var map = L.map(mapNode, {
        worldCopyJump: true,
        minZoom: 2,
        maxZoom: 7
    }).setView(defaultView.center, defaultView.zoom);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    var layersByKind = {
        visited: L.layerGroup().addTo(map),
        mug: L.layerGroup().addTo(map)
    };

    var positionUseCount = {};

    function escapeHtml(value) {
        return String(value || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function staticUrlFromRelative(path) {
        var current = window.location.origin || "";
        return current + "/static/" + String(path || "").replace(/^\/+/, "");
    }

    function buildPopupHtml(point) {
        var notes = Array.isArray(point.notes) ? point.notes.filter(Boolean) : [];
        var subtitleLine = "";
        var notesHtml = "";

        if (point.kind === "mug") {
            subtitleLine = point.gifted_by ? ("by " + escapeHtml(point.gifted_by)) : "Starbucks mug";
        } else if (notes.length === 1) {
            subtitleLine = escapeHtml(notes[0]);
        } else if (notes.length > 1) {
            subtitleLine = "Trips / memories";
            notesHtml = "<ul class='travel-popup-notes'>" + notes.map(function (note) {
                return "<li>" + escapeHtml(note) + "</li>";
            }).join("") + "</ul>";
        } else {
            subtitleLine = "Visited";
        }

        return (
            "<div class='travel-popup'>" +
                "<p class='travel-popup-title'>" + escapeHtml(point.title) + "</p>" +
                "<p class='travel-popup-subtitle'>" + subtitleLine + "</p>" +
                notesHtml +
            "</div>"
        );
    }

    var selectionPanel = document.getElementById("map-selection-panel");
    var travelsLayout = document.getElementById("travels-layout");

    function buildSelectionPanelHtml(point) {
        if (!point) {
            return "<p class='map-selection-empty mb-0'>Click a pin to preview it here.</p>";
        }

        var notes = Array.isArray(point.notes) ? point.notes.filter(Boolean) : [];
        var photos = Array.isArray(point.photos) ? point.photos.filter(function (photo) {
            return photo && photo.path;
        }) : [];
        var line = "";
        var notesHtml = "";
        var photoHtml = "";

        if (point.kind === "mug") {
            line = point.gifted_by ? ("by " + escapeHtml(point.gifted_by)) : "Starbucks mug";
        } else if (notes.length === 1) {
            line = escapeHtml(notes[0]);
        } else if (notes.length > 1) {
            line = "Trips / memories";
            notesHtml = "<ul class='map-selection-list'>" + notes.map(function (note) {
                return "<li>" + escapeHtml(note) + "</li>";
            }).join("") + "</ul>";
        } else {
            line = "Visited";
        }

        if (photos.length) {
            var photo = photos[0];
            photoHtml =
                "<figure class='map-selection-photo'>" +
                    "<img id='map-selection-photo' src='" + escapeHtml(staticUrlFromRelative(photo.path)) + "' alt='" + escapeHtml(photo.alt || point.title) + "' loading='lazy'>" +
                    (photo.caption ? ("<figcaption>" + escapeHtml(photo.caption) + "</figcaption>") : "") +
                "</figure>";
        }

        return (
            "<div>" +
                "<p class='map-selection-title'>" + escapeHtml(point.title) + "</p>" +
                "<p class='map-selection-line'>" + line + "</p>" +
            "</div>" +
            notesHtml +
            photoHtml
        );
    }

    function renderSelectionPanel(point) {
        var hasPhoto = !!(
            point &&
            Array.isArray(point.photos) &&
            point.photos.some(function (photo) {
                return photo && photo.path;
            })
        );

        if (travelsLayout) {
            travelsLayout.classList.toggle("has-selection-photo", hasPhoto);
        }

        if (!selectionPanel) {
            return;
        }
        selectionPanel.innerHTML = buildSelectionPanelHtml(point);
        var panelPhoto = selectionPanel.querySelector("#map-selection-photo");
        if (panelPhoto) {
            panelPhoto.addEventListener("error", function () {
                var figure = panelPhoto.closest(".map-selection-photo");
                if (figure) {
                    figure.remove();
                }
            }, { once: true });
        }
    }

    points.forEach(function (point) {
        var kind = point.kind === "mug" ? "mug" : "visited";
        var key = point.lat.toFixed(2) + "," + point.lng.toFixed(2);
        var used = positionUseCount[key] || 0;
        positionUseCount[key] = used + 1;

        // Slight offsets keep overlapping pins clickable when a location has both categories.
        var latOffset = (used % 3) * 0.22;
        var lngOffset = (kind === "mug" ? 0.25 : -0.18) + (Math.floor(used / 3) * 0.16);

        var marker = L.circleMarker([point.lat + latOffset, point.lng + lngOffset], {
            radius: kind === "mug" ? 7 : 6.5,
            color: colors[kind],
            weight: 2,
            fillColor: colors[kind],
            fillOpacity: 0.82
        });

        marker.bindPopup(buildPopupHtml(point), { maxWidth: 280 });
        marker.on("click", function () {
            renderSelectionPanel(point);
        });
        marker.addTo(layersByKind[kind]);
    });

    var toggleVisited = document.getElementById("toggle-visited");
    var toggleMugs = document.getElementById("toggle-mugs");
    var resetButton = document.getElementById("reset-map-view");

    function syncLayer(toggle, kind) {
        if (!toggle) {
            return;
        }
        if (toggle.checked) {
            if (!map.hasLayer(layersByKind[kind])) {
                map.addLayer(layersByKind[kind]);
            }
        } else if (map.hasLayer(layersByKind[kind])) {
            map.removeLayer(layersByKind[kind]);
        }
    }

    if (toggleVisited) {
        toggleVisited.addEventListener("change", function () {
            syncLayer(toggleVisited, "visited");
        });
    }
    if (toggleMugs) {
        toggleMugs.addEventListener("change", function () {
            syncLayer(toggleMugs, "mug");
        });
    }
    if (resetButton) {
        resetButton.addEventListener("click", function () {
            map.setView(defaultView.center, defaultView.zoom, { animate: true });
        });
    }

    renderSelectionPanel(null);

    var galleryNode = document.getElementById("travel-gallery-data");
    var gallery = [];
    if (galleryNode) {
        try {
            gallery = JSON.parse(galleryNode.textContent || "[]");
        } catch (err) {
            gallery = [];
        }
    }

    gallery.forEach(function (photo) {
        var img = document.getElementById(photo.img_id);
        var fallback = document.getElementById(photo.fallback_id);
        if (!img || !fallback) {
            return;
        }

        var candidates = Array.isArray(photo.fallback_paths) ? photo.fallback_paths.slice() : [];

        img.addEventListener("error", function () {
            if (candidates.length) {
                img.src = staticUrlFromRelative(candidates.shift());
                return;
            }
            img.hidden = true;
            fallback.hidden = false;
        });
    });

})();
