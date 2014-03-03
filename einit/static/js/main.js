require.config({
  baseUrl: '/vendor',
  paths: {
    js: '../js',
    models: '../models',
    views: '../views',
    templates: '../templates'
  },
  shim: {
    'marionette': {
      deps: [ 'backbone' ],
      exports: 'Marionette'
    },
    'backbone': {
      deps: [ 'underscore', 'jquery' ],
      exports: 'Backbone'
    },
    'underscore': {
      exports: '_'
    },
    'jquery': {
      exports: '$'
    },
    'handlebars': {
      exports: 'Handlebars'
    },
    {
    'bootstrap': {
      exports: '$'
    }
    }
  },
  deps: [ 'js/app' ]
});