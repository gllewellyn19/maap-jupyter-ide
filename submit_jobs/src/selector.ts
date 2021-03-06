import { Widget } from '@lumino/widgets';
import { PageConfig } from '@jupyterlab/coreutils'
//import { INotification } from 'jupyterlab_toastify';
// import { getUserInfo } from './getKeycloak';
import { request, RequestResult } from './request';
import { InputWidget, RegisterWidget } from './widgets';
import { getAlgorithms, getDefaultValues, inputRequest } from './funcs';
import { popup, popupResult } from "./dialogs";
import { IStateDB } from '@jupyterlab/statedb';

// popup helper for register to select project
export class DropdownSelector extends Widget {
  type: string;
  _fields: string[];
  _username:string;
  _ticket: string;
  public selection:string;
  _dropdown: HTMLSelectElement;
  _state: IStateDB;

  constructor(type, fields, uname, ticket, state) {
    super();
    this._fields = fields;
    this._username = uname;
    this._ticket = ticket;
    this.type = type;
    this._state = state;

    this._dropdown = <HTMLSelectElement>document.createElement("SELECT");
    this._dropdown.id = "project-dropdown";
    this._dropdown.setAttribute("style", "font-size:20px;");

    if (type === 'register') {
      this.getProjects().then((projectList) => {
        // console.log(projectList);
        var opt:HTMLOptionElement;
        var txt:string;
        for (var file of projectList) {
          var lang = '';
          if (file.indexOf('.py') > -1 || file.indexOf('.ipynb') > -1) {
            lang = 'python';
          } else if (file.indexOf('.sh') > -1) {
            lang = 'bash';
          } else if (file.indexOf('.jl') > -1) {
            lang = 'julia';
          } else {
            lang = 'unknown';
            console.log('language unknown');
          }
          console.log('lang is '+lang);

          opt = <HTMLOptionElement>document.createElement("option");
          opt.setAttribute("id",file);
          txt = file+' (' + lang +')';
          opt.setAttribute("label",txt);
          opt.appendChild(document.createTextNode(txt));
          this._dropdown.appendChild(opt);
        }
        this.node.appendChild(this._dropdown);
      });
    } else if (['describeProcess','publishAlgorithm','executeInputs','deleteAlgorithm'].includes(type)) {
      let me = this;
      console.log('getAlgorithms');
      
      getAlgorithms(this._state, this._ticket).then((algo_lst:{[k:string]:Array<string>}) => {
        if (Object.keys(algo_lst).length == 0) {
          me.selection = "No algorithms available";
        }
        var opt:HTMLOptionElement;
        var txt:string;
        // console.log(algo_lst);
        for (var algo in algo_lst) {
          for (var ver of algo_lst[algo]) {
            txt = algo+':'+ver;
            opt = <HTMLOptionElement>document.createElement("option");
            opt.setAttribute("id",txt);
            opt.setAttribute("label",txt);
            opt.appendChild(document.createTextNode(txt));
            this._dropdown.appendChild(opt);
          }
          console.log('appending '+algo);
        }
        this.node.appendChild(this._dropdown);
      });
    }
  }

  getProjects() {
    var me = this;
    return new Promise<Array<string>>((resolve, reject) => {
      var projectList: Array<string> = []

      // get list of projects to give dropdown menu
      var settingsAPIUrl = new URL(PageConfig.getBaseUrl() + 'pull_projects/listFiles');
      console.log(settingsAPIUrl.href);
      request('get',settingsAPIUrl.href).then((res: RequestResult) => {
        console.log(res);
        if (res.ok) {
          var json_response:any = res.json();
          console.log(json_response);
          var projects = json_response['project_files'];
          if (projects.length == 0) {
            me.selection = "No open notebooks";
            return;
          } else {
            projectList = projects;
          }
        resolve(projectList);
        }
      });
    });
  }

  // loadUserProxyTicket() {
  //   return new Promise(function(resolve, reject) {
  //       getUserInfo(function(profile:any) {
  //         if (profile['proxyGrantingTicket'] !== undefined) {
  //           console.log(`Loaded proxy ticket ${profile['proxyGrantingTicket']}`);
  //           resolve(profile['proxyGrantingTicket']);
  //         } else {
  //           reject(new Error('Error retrieving proxy ticket'));
  //         }
  //       });
  //   });
  // }

  // overrides resolution of popup dialog
  getValue() {
    // var ind = this._dropdown.selectedIndex;
    let opt:string = this._dropdown.value;
    let ind = opt.indexOf('(');
    if (ind > -1) {
      opt = opt.substr(0,ind).trim();
    }
    console.log(opt);
    
    // guarantee RegisterWidget is passed a value
    if (opt == null || opt == '') {
      console.log('no option selected');
      popupResult("No Option Selected","Select Failed");

    // these calls all require just params algo_id, version
    } else if (this.type == 'describeProcess' || this.type == 'publishAlgorithm' || this.type == 'executeInputs' || this.type == 'deleteAlgorithm') {
      let lst = opt.split(':');
      let algo_id = lst[0];
      let version = lst[1];

      if (this.type == 'executeInputs'){
        let me = this;
        // define function callback to be run after evaluation of selection
        let fn = function(resp:{[k:string]:(string|string[]|{[k:string]:string})}) {
          console.log('resp');
          var new_fields = resp['ins'] as string[];
          var predefined_fields = resp['old'] as {[k:string]:string};
          console.log(predefined_fields);
          var exec = new InputWidget('execute',new_fields,me._username,me._ticket,{});
          exec.setPredefinedFields(predefined_fields);
          exec.popupTitle = algo_id+':'+version;
          popup(exec);
        }
        inputRequest(this._state, this.type,algo_id,{'algo_id':algo_id,'version':version,'username':this._username,'proxy-ticket':this._ticket},fn);

        // no additional user action required after selection
      } else {
        inputRequest(this._state, this.type,algo_id,{'algo_id':algo_id,'version':version,'username':this._username,'proxy-ticket':this._ticket});
      }

    } else if (this.type == 'register') {
      getDefaultValues(opt).then((defaultValues) => {
        console.log(defaultValues);
        console.log('create register');
        let w = new RegisterWidget(this._fields,this._username,this._ticket,defaultValues);
        w.setPredefinedFields(defaultValues);
        console.log(w);
        popup(w);
      });
    }
    return;
  }
}
