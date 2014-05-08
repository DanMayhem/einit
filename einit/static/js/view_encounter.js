var EncounterModel = Backbone.Model.extend({
  defaults: {
    title: '',
    round: 0,
    events:[]
  },
  url: '/observe/'+get_encounter_hash()+".json"
});

var EntryModel = Backbone.Model.extend({
});

var EntryCollection = Backbone.Collection.extend({
  model: EntryModel
});

var EntryView = Marionette.ItemView.extend({
  tagName: 'li',
  className: 'list-group-item',
  template: _.template( $( '#entry-template' ).html() ),
});

var EncounterView = Marionette.CompositeView.extend({
  template: _.template( $( '#encounter-template' ).html() ),
  className: 'panel panel-primary',
  itemView: EntryView,
  itemViewContainer: 'ul',
  initialize: function(){
    this.collection = this.model.get('entry_list');
  }
});

app = new Backbone.Marionette.Application()

app.addRegions({
  mainRegion: '.app-main-content'
});

app.encounter = new EncounterModel();

app.encounter.fetch({
  success: function(){
    var entries = app.encounter.get("entries")
    var entryCollection = new EntryCollection(entries)
    app.encounter.set("entry_list",entryCollection)
    app.mainRegion.show(new EncounterView({
      model:app.encounter
    }))
  }
});
