define(function( require ) {
    "use strict";

    // imports
    var _ = require( 'underscore' );
    var Backbone = require( 'backbone' );
    var Marionette = require( 'marionette' );
    var GameLayout = require( 'views/game-layout' );
    var GameModel = require( 'models/game' );

    // locals
    var game = new Marionette.Application();

    var GameController = Marionette.Controller.extend({
    });

    var GameRouter = Marionette.AppRouter.extend({
        controller: new GameController()
    });

    game.addInitializer( function( options ) {
        game.addRegions( {
            body: 'body'
        });

        game.model = new GameModel();
        game.model.fetch( {
            success: function() {

                console.log( game.model );

                game.body.show( new GameLayout({
                    model: game.model
                }) );

                game.router = new GameRouter();

                Backbone.history.start();

            }
        });
    } );

    game.start();
});