/* global define, jQuery */
(
    $('#id_version').change(function(){
        $('#id_taxon').val(null).trigger('change');
    }))