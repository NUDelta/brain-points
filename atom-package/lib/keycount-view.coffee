{Disposable, CompositeDisposable} = require 'atom'
{$$, View} = require 'atom-space-pen-views'
$ = require 'jquery'

module.exports =
class KeycountView extends View
  @content: ->
    @div class: 'key-count-resolver', =>
      @div class: 'panel-heading padded', =>
        @div class: 'block', =>
          @span class: 'keycount-menu', 'Currently Recording Keystrokes'
          @button class: 'inline-block-tight stop', "Stop Recording"
          @span class: 'keycount-menu-points', outlet: "pointcount", " 0 "
          @span class: 'keycount-menu-points', 'Brain Points:'
      @div outlet: 'keylist', class: 'panel-body padded'

  add: (keys) ->
    r=@run
    lp=@lastpause
    lk=@lastkey
    check=@comment
    t = Date.now()
    # detect print statement
    last=@last5
    print=@printed

    #detect phrase
    @last5.push(keys)

    if @last5.length == 5
      if @last5.join("") == 'print'
        if t - @printed > 60000
          atom.notifications.addSuccess "Debugging with print statements is a great way to understand your code! +1"
          @points++
          @printed = t
      @last5.shift()

    # pause stuff
    @lastkey = t
    if t-lk > 30000
      @lastpause = t
      @comment = 1

    if(lk-lp > 300000)
      atom.notifications.addWarning "Take a step back to think about what you're typing"
      @lastpause = t

    if keys == '#' && check == 1
      atom.notifications.addSuccess "Great job thinking through the problem! +1"
      @points++
      @comment = 0
      #running stuff
    if r.length > 0
      if t-r[0] > 30000
        r.pop(0)
      if keys== 'cmd-i'
        if r.length >= 3
          atom.notifications.addWarning("Think about what your code will output before running it.")
          r.push([Date.now()])
          @run=[]
      if keys== 'shift-ctrl-b'
        if r.length >= 3
          atom.notifications.addWarning("Think about what your code will output before running it.")
          r.push([Date.now()])
          @run=[]


    @count++
    @history = @history[-2..]
    @history.push keys
    @refresh()

  refresh: () ->
    p=@points
    @pointcount.html $$ ->
      @span class: 'keycount'," " + p
    c = @count
    history = @history
    time = Date.now()
    fs = require 'fs'
    editor = atom.workspace.getActivePaneItem()
    file = editor?.buffer.file
    directory = file?.getParent()
    dirPath = directory?.path
    fs.appendFile dirPath + '/keystrokes.csv', time + ',' + history[-1..] + '\n'


  initialize: ->
    @count = 0
    @points = 0
    @history = []
    @run = []
    @lastpause=Date.now()
    @lastkey=Date.now()
    @comment = 1
    @last5 = []
    # subtract 60 seconds to make sure we can detect if the first print occurs within the first minutes
    @printed= Date.now()-60000
    @on 'click', '.stop', ({target}) => @detach()

  # Tear down any state and detach
  destroy: ->

  serialize: ->
    attached: @panel?.isVisible()

  toggle: ->
    if @panel?.isVisible()
      @detach()
    else
      @attach()
      @time = Date.now()

  reset: ->
    @count = 0
    @history = []
    @refresh()

  attach: ->
    @disposables = new CompositeDisposable

    @panel = atom.workspace.addBottomPanel(item: this)
    @disposables.add new Disposable =>
      @panel.destroy()
      @panel = null

    @disposables.add atom.keymaps.onDidMatchBinding ({keystrokes, binding, keyboardEventTarget}) =>
      @update(keystrokes)

    @disposables.add atom.keymaps.onDidPartiallyMatchBindings ({keystrokes, partiallyMatchedBindings, keyboardEventTarget}) =>
      @update(keystrokes)

    @disposables.add atom.keymaps.onDidFailToMatchBinding ({keystrokes, keyboardEventTarget}) =>
      @update(keystrokes)

  detach: ->
    @disposables?.dispose()

  update: (keystrokes) ->
    if (keystrokes[0] != '^')
      @add keystrokes
