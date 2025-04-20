/**
 * CKAN ClamAV scan file
 */
ckan.module("clamav-scan-file", function ($, _) {
    "use strict";

    return {
        initialize: function () {
            $.proxyAll(this, /_/);

            this.form = $("#resource-edit");

            if (!this.form) {
                console.log('clamav: no form found, skipping');
                return;
            }

            // add event listener
            this.form.find("input[type='file']").on('change', this._onFileChange);

            // on init
            this._appendTokenField();
        },

        _appendTokenField: function () {
            this.tokenField = $('<input>').attr({
                type: 'hidden',
                name: 'clamav_token',
            }).appendTo(this.form);
        },

        _onFileChange: function (e) {
            if (e.target.files.length === 0) {
                return;
            }

            this._onStartScan();

            const self = this;
            const file = e.target.files[0];

            const formData = new FormData();
            formData.append("upload", file);
            formData.append("size", file.size);
            var csrf_field = $('meta[name=csrf_field_name]').attr('content');
            var csrf_token = $('meta[name=' + csrf_field + ']').attr('content');

            $.ajax({
                method: 'POST',
                url: this.sandbox.client.url('/api/action/clamav_scan_file'),
                data: formData,
                cache: false,
                contentType: false,
                processData: false,
                headers: {
                    'X-CSRFToken': csrf_token
                },
                success: function (data) {
                    console.log(data);
                    if (data.result.success) {
                        self._onScanSuccess(data.result);
                    } else {
                        self._onScanError(data.result);
                    }
                },
            });
        },

        _onStartScan: function () {
            this._toggleFormSubmit(true);
            this.el.find('.info').text('Scanning...');

            this.el.find('.spinner').show();
            this.el.show();
        },

        _onScanSuccess: function (data) {
            this.tokenField.attr("value", data.token);

            this._toggleFormSubmit(false);
            this.el.find('.info').text('');
            this.el.find('.spinner').hide();
            this.el.hide();
        },

        _onScanError: function (data) {
            this.tokenField.attr("value", "");

            this._toggleFormSubmit(false);
            this.el.find('.info').text(data.error);
            this.el.find('.spinner').hide();
        },

        _toggleFormSubmit: function (disabled) {
            this.form.find('button[type="submit"]').prop('disabled', disabled);
        },
    };
});
