import { Widget } from '@lumino/widgets';
import { PageConfig } from '@jupyterlab/coreutils'
import { INotification } from 'jupyterlab_toastify';
// import { getUserInfo } from "./getKeycloak";
import { popupTitle, popupResult } from './dialogs';
import { request, RequestResult } from './request';

// -----------------------
// HySDS endpoints that require user inputs
// -----------------------
const nonXML: string[] = ['register','execute','getStatus','getMetrics','getResult','dismiss','delete'];
const notImplemented: string[] = [];

export class InputWidget extends Widget {

  // TODO: protect instance vars
  public readonly req: string;
  public popupTitle: string;
  public predefinedFields: Object;        // store predefined fields (default values)
  public readonly fields: string[];       // user inputs to fill out
  public username: string;                // for execute & listing jobs in case of timeout
  _ticket: string;                        // proxy ticket for authenticating user-specific actions
  _responseText: string;                  // request response to display in popup or widget
  _getInputs: boolean;                    // for getting predefinedFields
  _ins_dict: {[k:string]:string};         // for execute

  constructor(req:string,methodFields:string[],uname:string,ticket:string,defaultValues:Object,skipInputs?:boolean) {
    let body = document.createElement('div');
    body.style.display = 'flex';
    body.style.flexDirection = 'column';
    super({node: body});

    // Default text
    this.req = req;
    this.predefinedFields = defaultValues;
    this.fields = methodFields;
    this.username = uname;
    this._ticket = ticket;
    this._responseText = "";
    this._getInputs = false;
    this._ins_dict = {};

    switch (req) {
      case 'register':
        this.popupTitle = "Register Algorithm";
        console.log('register');
        break;
      case 'execute':
        this.popupTitle = "Execute Job - Provide Inputs";
        this._getInputs = true;
        console.log('execute');
        break;
      case 'getStatus':
        this.popupTitle = "Get Job Status";
        console.log('getStatus');
        break;
      case 'getMetrics':
        this.popupTitle = "Get Job Metrics";
        console.log('getMetrics');
        break;
      case 'getResult':
        this.popupTitle = "Get Job Result";
        console.log('getResult');
        break;
      case 'dismiss':
        this.popupTitle = "Dismiss Job";
        console.log('dismiss');
        break;
      case 'delete':
        this.popupTitle = "Delete Job";
        console.log('delete');
        break;
    }
    // console.log(this.fields);

    // bind method definitions of "this" to refer to class instance
    this.getValue = this.getValue.bind(this);
    this.updateSearchResults = this.updateSearchResults.bind(this);
    this.setPredefinedFields = this.setPredefinedFields.bind(this);
    this._buildRequestUrl = this._buildRequestUrl.bind(this);

    // skip 1st popup if nothing to fill out
    if ( typeof this.fields === "undefined" || this.fields.length == 0) {
      let body = document.createElement('div');
      body.style.display = 'flex';
      body.style.flexDirection = 'column';

      var label = document.createElement("Label");
      label.innerHTML = "No inputs required";
      this.node.appendChild(label);
      body.appendChild(label);
      this.node.appendChild(body);
      return;
    }

    // BREAK
    var x = document.createElement("BR");
    this.node.appendChild(x)

    if (skipInputs == undefined || skipInputs == false) {
      // TODO enforce input types
      // Construct labels and inputs for fields
      for (var field of this.fields) {
        var fieldName;
        if (typeof(field) == "string"){
          fieldName = field;
        } else {
          fieldName = field[0];
        }
        if (fieldName != 'inputs' && fieldName != 'proxy-ticket' && fieldName != 'username') {
          var fieldLabel = document.createElement("Label");
          fieldLabel.innerHTML = fieldName;
          this.node.appendChild(fieldLabel);
  
          fieldName = fieldName.toLowerCase();
          var fieldInput = document.createElement('input');
          fieldInput.id = (fieldName + '-input');
          fieldInput.classList.add(fieldName);
          if (field in defaultValues) {
            fieldInput.value = defaultValues[field] as string;
          }
          this.node.appendChild(fieldInput);
        
          // // newline
          // var br = document.createElement("BR");
          // this.node.appendChild(br);
  
          // // add button
          // var fieldAdd = document.createElement('button');
          // fieldAdd.innerHTML = 'Add Run Input';
          // fieldAdd.id = (fieldName + '-add');
          // fieldAdd.name = fieldName;
          // fieldAdd.addEventListener('click', (e:Event) => this._insertField(e), false);
          // this.node.appendChild(fieldAdd);
  
          // newline
          var br = document.createElement("BR");
          this.node.appendChild(br);
        }
      }
      // console.log('done constructing');
    }
  }

  // _insertField(fieldName:string) {
  _insertField(e:Event) {
    console.log('adding field '+fieldName);
    var fieldName = (<HTMLButtonElement>e.currentTarget).name;
    fieldName = fieldName.toLowerCase();
    var addbtn = document.getElementById(fieldName+'-add');
    var fieldInput = document.createElement('input');
    fieldInput.id = (fieldName + '-input');
    fieldInput.classList.add(fieldName);

     // insert newline & new input field before add button
    addbtn.parentNode.insertBefore(document.createElement("BR"),addbtn.previousSibling);
    addbtn.parentNode.insertBefore(fieldInput,addbtn.previousSibling);
    return;
  }

  setPredefinedFields(old:Object): void {
    console.log('setting fields');
    this.predefinedFields = old;
    // TODO enforce input types
  }

  updateSearchResults(): void {
    // document.getElementById('search-text').innerHTML = this._responseText;
    if (document.getElementById('result-text') != null){
      // console.log('using textarea');
      (<HTMLDivElement>document.getElementById('result-text')).innerHTML = "<pre>" + this._responseText + "</pre>";
    } else {
      // console.log('create textarea');
      popupResultText(this._responseText,"Results",(!nonXML.includes(this.req)));
    }
  }

  // helper to deepcopy aka rebuild URL for execute because deepcopy is a pain rn
  buildCopyUrl(fieldName:string,fieldValue:string): URL {
    var getUrl = new URL(PageConfig.getBaseUrl() + 'hysds/'+this.req);
    // only call when passed inputs not provided by user
    if (this._getInputs) {
      // filling out algo info (id, version)
      for (let key in this.predefinedFields) {
        var fieldText = (this.predefinedFields[key] as string).toLowerCase();
        getUrl.searchParams.append(key.toLowerCase(), fieldText);
      }
      // filling out algo inputs
      var new_input_list = "";

      for (var e of this.fields) {
        var field = e[0].toLowerCase();
        new_input_list = new_input_list.concat(field,',');
        if (fieldName == field){
          getUrl.searchParams.append(field.toLowerCase(), fieldValue);
        } else {
          var fieldText = (<HTMLInputElement>document.getElementById(field.toLowerCase()+'-input')).value;
          this._ins_dict[field] = fieldText;
          getUrl.searchParams.append(field.toLowerCase(), fieldText);
        }
      }
      getUrl.searchParams.append("inputs",new_input_list);
      getUrl.searchParams.append('username',this.username);
      console.log('added username '+fieldValue);
      // console.log(getUrl.href);
    }
    return getUrl;
  }

  _buildRequestUrl() {
    var me:InputWidget = this;
    return new Promise<Array<URL>>(async (resolve, reject) => {
      // create API call to server extension
      var urllst: Array<URL> = []
      var getUrl = new URL(PageConfig.getBaseUrl() + 'hysds/'+this.req);

      // filling out old fields, currently for algo info (id, version) in execute & describe & delete
      if (this._getInputs) {
        // console.log('get predefined fields');
        for (let key in this.predefinedFields) {
          // console.log(key);
          var fieldText = (this.predefinedFields[key] as string).toLowerCase();
          getUrl.searchParams.append(key.toLowerCase(), fieldText);
        }
      }

      // always add username
      getUrl.searchParams.append('username',this.username);

      // for calling execute after getting user inputs
      if (this.req == 'execute') {
        // filling out algo inputs
        var new_input_list = "";
        var range = false;
        var rangeField = "";
        var rangeFieldValue:string[] = [];

        if ( typeof this.fields != "undefined" && this.fields.length >= 0) {
          for (var e of this.fields) {
            var field = e[0].toLowerCase();
            new_input_list = new_input_list.concat(field,',');
            // console.log(field);
            var fieldText = (<HTMLInputElement>document.getElementById(field.toLowerCase()+'-input')).value;
            // console.log(fieldText);

            // check for range in inputs
            // currently only support INTEGER range in SINGLE input field
            // expected format "range:1:10"
            if (fieldText.includes("range:")) {
              range = true;
              rangeField = field;
              rangeFieldValue = fieldText.split("range:")[1].split(":");
            }
            this._ins_dict[field] = fieldText;
            getUrl.searchParams.append(field.toLowerCase(), fieldText);
          }
          console.log(new_input_list);
          getUrl.searchParams.append("inputs",new_input_list);
          
          // if multiple runs over one input
          if (range) {
            var start = Number(rangeFieldValue[0]);
            var last = Number(rangeFieldValue[1]);
            console.log(rangeFieldValue);
            // var len = last - start + 1;
            for (var i = start; i <= last; i++) {
              let multiUrl = this.buildCopyUrl(rangeField,String(i));
              console.log(multiUrl.href);
              urllst.push(multiUrl);
            }
            resolve(urllst);

          // just 1 job
          } else {
            console.log(getUrl.href);
            urllst.push(getUrl);
            resolve(urllst);
          }
        } else {
          console.log(getUrl.href);
          urllst.push(getUrl);
          resolve(urllst);
        }


      } else if (me.req == 'register') {
        resolve(urllst);

      // for all other requests
      } else {
        for (var field of this.fields) {
          if (field == 'inputs') {
            var fieldElement:HTMLElement = document.getElementById(field.toLowerCase()+'-input');
            var fieldText = (<HTMLTextAreaElement>fieldElement).value;
            getUrl.searchParams.append(field.toLowerCase(), fieldText);
          } else if (field == 'proxy-ticket') {
            getUrl.searchParams.append('proxy-ticket',this._ticket);
          } else if (field != 'username') {
            var fieldElement:HTMLElement = document.getElementById(field.toLowerCase()+'-input');
            var fieldText = (<HTMLInputElement>fieldElement).value;
            getUrl.searchParams.append(field.toLowerCase(), fieldText);
          }
        }
        console.log(getUrl.href);
        urllst.push(getUrl);
        resolve(urllst);
      }

    });
  }

  _sendRequest(urllst:Array<URL>) {
    this._responseText = '';
    for (var ind in urllst){
      var getUrl = urllst[ind];
      console.log(getUrl.href);
      var me:InputWidget = this;
      // Send Job as Request
      // set result text to response
      if ( !(notImplemented.includes(me.req) )){
        request('get', getUrl.href).then((res: RequestResult) => {
          if(res.ok){
            let json_response:any = res.json();
            // console.log(json_response);
            me._responseText = me._responseText + '\n' + json_response['result'];
            if (json_response['status_code'] != 200) {
              INotification.error(me._responseText);
            }
          } else {
            let json_response:any = res.json();
            // console.log(json_response);
            me._responseText = "Error Sending Request:\n" + json_response['result'];
            INotification.error(me._responseText);
          }
          console.log("updating");
          me.updateSearchResults();
        });
      } else {
        console.log("not implemented yet");
      }
    }
    return;
  }

  // submit the job
  // overrides the resolution of popup dialog
  getValue(): void {
    this._buildRequestUrl().then((url) => {
      console.log(url);
      this._sendRequest(url);
    });
  }
}

export class RegisterWidget extends InputWidget {
  configPath: string;

  constructor(methodFields:string[],uname:string,ticket:string,defaultValues:Object,subtext?:string,configPath?:string) {
    super('register', methodFields,uname,ticket,defaultValues,true);
    this.configPath = configPath;


    // bind method definitions of "this" to refer to class instance
    this.getValue = this.getValue.bind(this);
    this.updateSearchResults = this.updateSearchResults.bind(this);
    this.setPredefinedFields = this.setPredefinedFields.bind(this);
    this._buildRequestUrl = this._buildRequestUrl.bind(this);

    if (subtext != undefined) {
      let subtxt = document.createElement('p');
      subtxt.id = 'register-subtext';
      subtxt.style.display = 'flex';
      subtxt.style.flexDirection = 'column';
      subtxt.innerHTML = subtext;
      this.node.appendChild(subtxt);
      this.node.appendChild(document.createElement('BR'));
    }

    for (let field of this.fields) {
        // textarea for inputs field in register
        if (field === 'inputs') {
            setTimeout(() => {  
                let fieldLabel = document.createElement('Label');
                fieldLabel.innerHTML = field;
                this.node.appendChild(fieldLabel);

                let fieldInputs = document.createElement('textarea');
                fieldInputs.id = (field.toLowerCase() + '-input');
                (<HTMLTextAreaElement>fieldInputs).cols = 40;
                (<HTMLTextAreaElement>fieldInputs).rows = 6;

                // show input names and dl
                let ins = ''
                for (let itm of (defaultValues['inputs'] as Array<{[k:string]:string}>)) {
                ins = ins+itm['name'];
                if (itm['download']) {
                    ins = ins+' (download)';
                } else {
                    ins = ins+' (no download)';
                }
                ins = ins+'\n';
                }
                fieldInputs.value = ins;
                fieldInputs.readOnly = true;
                this.node.appendChild(fieldInputs);
            }, 500);
        
        } else if (field === 'queue') {
            let fieldLabel = document.createElement('Label');
            fieldLabel.innerHTML = field;
            this.node.appendChild(fieldLabel);

            let fieldInputs = document.createElement("SELECT");
            fieldInputs.id = "queues-dropdown";
            fieldInputs.setAttribute("style", "font-size:14px;");

            let getUrl = new URL(PageConfig.getBaseUrl() + 'hysds/getQueues')
            request('get', getUrl.href).then((res) => {
                let json_response:any = res.json();
                console.log(json_response);
                let qs = json_response['result'];
                let opt:HTMLOptionElement;
                for (let q of qs) {
                    opt = <HTMLOptionElement>document.createElement("option");
                    opt.setAttribute("id", q);
                    opt.setAttribute("label", q);
                    opt.appendChild(document.createTextNode(q));
                    fieldInputs.appendChild(opt);
                }
                this.node.appendChild(fieldInputs);
            });
        } else {
            let fieldLabel = document.createElement('Label');
            fieldLabel.innerHTML = field;
            this.node.appendChild(fieldLabel);

            let fieldInput = document.createElement('input');
            fieldInput.id = (field.toLowerCase() + '-input');
            // set default values
            if (field in defaultValues) {
                fieldInput.value = defaultValues[field] as string;
            }
            fieldInput.readOnly = true;
            this.node.appendChild(fieldInput);
        }
    }

    setTimeout(() => {  
        // BREAK
        var x = document.createElement('BR');
        this.node.appendChild(x)
    
        // footer text - edit config at path
        let editFooter = document.createElement('p');
        editFooter.id = 'configpath-subtext';
        editFooter.style.display = 'flex';
        editFooter.style.flexDirection = 'column';
        editFooter.innerHTML = 'To modify the configuration, click "Cancel" and modify the values in '+configPath;
        this.node.appendChild(editFooter);
    }, 500);
  }

  _buildRequestUrl() {
    // var me:RegisterWidget = this;
    return new Promise<Array<URL>>((resolve, reject) => {
        // create API call to server extension
        let urllst: Array<URL> = []
        let getUrl = new URL(PageConfig.getBaseUrl() + 'hysds/'+this.req);
        getUrl.searchParams.append('config_path', this.configPath);
        // add selected queue option
        let fieldElement:HTMLSelectElement = document.getElementById('queues-dropdown') as HTMLSelectElement;
        console.log(fieldElement);
        let opt:string = fieldElement.value;
        getUrl.searchParams.append('queue', opt);
        console.log(getUrl.href);
        console.log('done setting url');
        urllst.push(getUrl);
        resolve(urllst);
        });
    }
}

export class WidgetResult extends Widget {
  // pass InputWidget which contains info panel
  okfn: any;

  constructor(b: any, fn?:undefined) {
    super({node: b});
    // this.cache = jobsPanel;
    // this.updateCache = updateCache;
    this.okfn = fn;
  }

  // update panel text on resolution of result popup
  getValue() {
    console.log('checking popup resolution fn');
    if (typeof this.okfn === "function") {
      console.log(this.okfn);
      try{
        this.okfn();
      }
      catch (_e) {
        let e:Error = _e;
        console.log(e);
      }
    }
  }
}

// here because import dependencies of popupResult(dialog.ts), WidgetResult(widget.ts)
export function popupResultText(result:string,title:string,fn?:any,isXML?:boolean) {
  let body = document.createElement('div');
  body.style.display = 'flex';
  body.style.flexDirection = 'column';

  var textarea = document.createElement('div');
  textarea.id = 'result-text';
  textarea.style.display = 'flex';
  textarea.style.flexDirection = 'column';
  var format = require('xml-formatter');

  // console.log(result);
  if ( isXML === undefined || (! isXML) ){ 
    textarea.innerHTML = '<pre>' + result + '</pre>';
    // console.log(textarea);
  } else {
    var xml = '<root><content><p>'+result+'</p></content></root>';
    var options = {indentation: '  ', stripComments: true, collapseContent: false};
    var formattedXML = format(xml,options); 
    textarea.innerHTML = formattedXML;
    // console.log(formattedXML);
  }
  body.appendChild(textarea);
  // console.log(body);
  popupResult(new WidgetResult(body,fn),title);
}

// here because import dependencies of popupResult(dialog.ts), WidgetResult(widget.ts)
export function popupText(result:string,title:string,fn?:any) {
  let body = document.createElement('div');
  body.style.display = 'flex';
  body.style.flexDirection = 'column';

  var textarea = document.createElement('div');
  textarea.id = 'result-text';
  textarea.style.display = 'flex';
  textarea.style.flexDirection = 'column';

  // console.log(result);
  textarea.innerHTML = '<pre>' + result + '</pre>';
  body.appendChild(textarea);
  // console.log(body);
  if (fn === undefined) {
    popupTitle(new Widget({node:body}),title);
  } else {
    popupTitle(new WidgetResult(body,fn),title);
  }
}
