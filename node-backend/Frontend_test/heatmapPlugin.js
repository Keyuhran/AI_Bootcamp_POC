'use strict';

class HeatmapPlugin {
    _data = {};
    _options = {
        legend: true,
        timescale: true,
        range: {
            from: '#year#-01-01T00:00:00',
            till: '#year#-12-30T00:00:00',
            grade: 1,
            interval: 'day', //month, year, hours, minutes
            rows: 7,
        },
        units: 5
    };
    _theme = {
        width: '10',   // make bigger
        height: '10',
        font: {
            size: '12',
            family: 'Arial',
            color: 'black'
        }
    };
    _container = null;

    constructor(containerId, data, options = {}, theme = {}, instantRender = false){
        this._data = data;

        this.transferObject(options, this._options, 'range');
        this._options.range.from = this._options.range.from.replace(/#year#/i, new Date().getFullYear());
        this._options.range.till = this._options.range.till.replace(/#year#/i, new Date().getFullYear());
        this.transferObject(theme, this._theme, 'font');

        this._container = window.document.getElementById(containerId);
        if('undefined' === typeof(this._container))
            throw 'heatmap container '+containerId+' not found.';

        if(instantRender)
            this.render();
    }

    transferObject(src, dest, sub){
        if(src !== {}) {
            for (const [key, value] of Object.entries(src)) {
                if (key === 'colors')
                    for (const [rangeKey, rangeValue] of Object.entries(value)) {
                        dest[sub][rangeKey] = rangeValue;
                    }
                else
                    dest[key] = value;
            }
        }
    }

    render(){
        let unit;
        let html = '';
        let current = new Date(this._options.range.from);
        let target = new Date(this._options.range.till);

        while (current <= target) {
            unit = current.getDate() + '.' + (current.getMonth() + 1) + '.' + current.getFullYear() +
                'T' + current.getHours() + ':' + current.getMinutes() + ':' + current.getSeconds();
            html += '<div style="'+
                    'height: '+this._theme.height+'px; '+
                    'width: '+this._theme.width+'px; '+
                    '" class="entry color-';
            if (typeof this._data[unit] !== 'undefined') {
                const val = this._data[unit];
                const grade = Math.min(this._options.units - 1, Math.floor(val / 10));  // adjust bins if needed
                html += grade + `" title="${current.toLocaleDateString()} — ${val} interactions"`;
            } else {
                html += '0"';
                    }
            html += '></div>';

            switch (this._options.range.interval) {
                case 'day':
                    current.setDate(current.getDate() + this._options.range.grade);
                    break;
                case 'month':
                    current.setMonth(current.getMonth() + this._options.range.grade);
                    break;
                case 'hours':
                    current.setHours(current.getHours() + this._options.range.grade);
                    break;
                case 'minutes':
                    current.setMinutes(current.getMinutes() + this._options.range.grade);
                    break;
                case 'seconds':
                    current.setSeconds(current.getSeconds() + this._options.range.grade);
                    break;
                default:
                    current.setFullYear(current.getFullYear() + this._options.range.grade);
                    break;
            }
        }

        this._container.style.height = (this._theme.height*this._options.range.rows+(2*this._options.range.rows))+'px';
        this._container.innerHTML = html;

        if(this._options.legend)
            this.addLegend();
    }

    addLegend(){
        let legend = document.createElement('div');
        legend.className = 'heatmap-horizontal-legend';
        let html = 'less ';
        for(let option = 0; option < this._options.units; option++){
            html += '<div style="'+
                    'height: '+(this._theme.height/2)+'px; '+
                    'width: '+(this._theme.width/2)+'px; '+
                    '" class="entry color-'+
                    option+'"';
            html += '></div>';
        }
        html += ' many';
        legend.innerHTML = html;
        legend.style.color = this._theme.font.color;
        legend.style.fontSize = this._theme.font.size+'px';
        legend.style.fontFamily = this._theme.font.family;
        legend.style.marginTop = '20px';
        this._container.parentNode.insertBefore(legend, this._container.nextSibling);
    }
}
