import{E as t,r as e,_ as o,n as i,e as a,a as n,s,x as r,b as l,T as d,i as c,t as h,c as p,o as v,d as m,m as g}from"./matter-dashboard-app-DK7p6YeT.js";const u={dialog:[[[{transform:"translateY(-50px)"},{transform:"translateY(0)"}],{duration:500,easing:t.EMPHASIZED}]],scrim:[[[{opacity:0},{opacity:.32}],{duration:500,easing:"linear"}]],container:[[[{opacity:0},{opacity:1}],{duration:50,easing:"linear",pseudoElement:"::before"}],[[{height:"35%"},{height:"100%"}],{duration:500,easing:t.EMPHASIZED,pseudoElement:"::before"}]],headline:[[[{opacity:0},{opacity:0,offset:.2},{opacity:1}],{duration:250,easing:"linear",fill:"forwards"}]],content:[[[{opacity:0},{opacity:0,offset:.2},{opacity:1}],{duration:250,easing:"linear",fill:"forwards"}]],actions:[[[{opacity:0},{opacity:0,offset:.5},{opacity:1}],{duration:300,easing:"linear",fill:"forwards"}]]},b={dialog:[[[{transform:"translateY(0)"},{transform:"translateY(-50px)"}],{duration:150,easing:t.EMPHASIZED_ACCELERATE}]],scrim:[[[{opacity:.32},{opacity:0}],{duration:150,easing:"linear"}]],container:[[[{height:"100%"},{height:"35%"}],{duration:150,easing:t.EMPHASIZED_ACCELERATE,pseudoElement:"::before"}],[[{opacity:"1"},{opacity:"0"}],{delay:100,duration:50,easing:"linear",pseudoElement:"::before"}]],headline:[[[{opacity:1},{opacity:0}],{duration:100,easing:"linear",fill:"forwards"}]],content:[[[{opacity:1},{opacity:0}],{duration:100,easing:"linear",fill:"forwards"}]],actions:[[[{opacity:1},{opacity:0}],{duration:100,easing:"linear",fill:"forwards"}]]};class y extends s{get open(){return this.isOpen}set open(t){t!==this.isOpen&&(this.isOpen=t,t?(this.setAttribute("open",""),this.show()):(this.removeAttribute("open"),this.close()))}constructor(){super(),this.returnValue="",this.getOpenAnimation=()=>u,this.getCloseAnimation=()=>b,this.isOpen=!1,this.isOpening=!1,this.isConnectedPromise=this.getIsConnectedPromise(),this.isAtScrollTop=!1,this.isAtScrollBottom=!1,this.nextClickIsFromContent=!1,this.hasHeadline=!1,this.hasActions=!1,this.hasIcon=!1,this.escapePressedWithoutCancel=!1,this.addEventListener("submit",this.handleSubmit),this.addEventListener("focus",(()=>{var t;null===(t=this.dialog)||void 0===t||t.focus()})),this.addEventListener("blur",(()=>{var t;null===(t=this.dialog)||void 0===t||t.blur()}))}async show(){var t;this.isOpening=!0,await this.isConnectedPromise,await this.updateComplete;const e=this.dialog;if(e.open||!this.isOpening)return void(this.isOpening=!1);this.dispatchEvent(new Event("open",{cancelable:!0}))?(e.showModal(),this.open=!0,this.scroller&&(this.scroller.scrollTop=0),null===(t=this.querySelector("[autofocus]"))||void 0===t||t.focus(),await this.animateDialog(this.getOpenAnimation()),this.dispatchEvent(new Event("opened")),this.isOpening=!1):this.open=!1}async close(t=this.returnValue){if(this.isOpening=!1,!this.isConnected)return void(this.open=!1);await this.updateComplete;const e=this.dialog;if(!e.open||this.isOpening)return void(this.open=!1);const o=this.returnValue;this.returnValue=t;this.dispatchEvent(new Event("close",{cancelable:!0}))?(await this.animateDialog(this.getCloseAnimation()),e.close(t),this.open=!1,this.dispatchEvent(new Event("closed"))):this.returnValue=o}connectedCallback(){super.connectedCallback(),this.isConnectedPromiseResolve()}disconnectedCallback(){super.disconnectedCallback(),this.isConnectedPromise=this.getIsConnectedPromise()}render(){const t=this.open&&!(this.isAtScrollTop&&this.isAtScrollBottom),e={"has-headline":this.hasHeadline,"has-actions":this.hasActions,"has-icon":this.hasIcon,scrollable:t,"show-top-divider":t&&!this.isAtScrollTop,"show-bottom-divider":t&&!this.isAtScrollBottom},{ariaLabel:o}=this;return r`
      <div class="scrim"></div>
      <dialog
        class=${l(e)}
        aria-label=${o||d}
        aria-labelledby=${this.hasHeadline?"headline":d}
        role=${"alert"===this.type?"alertdialog":d}
        @cancel=${this.handleCancel}
        @click=${this.handleDialogClick}
        @close=${this.handleClose}
        @keydown=${this.handleKeydown}
        .returnValue=${this.returnValue||d}>
        <div class="container" @click=${this.handleContentClick}>
          <div class="headline">
            <div class="icon" aria-hidden="true">
              <slot name="icon" @slotchange=${this.handleIconChange}></slot>
            </div>
            <h2 id="headline" aria-hidden=${!this.hasHeadline||d}>
              <slot
                name="headline"
                @slotchange=${this.handleHeadlineChange}></slot>
            </h2>
            <md-divider></md-divider>
          </div>
          <div class="scroller">
            <div class="content">
              <div class="top anchor"></div>
              <slot name="content"></slot>
              <div class="bottom anchor"></div>
            </div>
          </div>
          <div class="actions">
            <md-divider></md-divider>
            <slot name="actions" @slotchange=${this.handleActionsChange}></slot>
          </div>
        </div>
      </dialog>
    `}firstUpdated(){this.intersectionObserver=new IntersectionObserver((t=>{for(const e of t)this.handleAnchorIntersection(e)}),{root:this.scroller}),this.intersectionObserver.observe(this.topAnchor),this.intersectionObserver.observe(this.bottomAnchor)}handleDialogClick(){if(this.nextClickIsFromContent)return void(this.nextClickIsFromContent=!1);!this.dispatchEvent(new Event("cancel",{cancelable:!0}))||this.close()}handleContentClick(){this.nextClickIsFromContent=!0}handleSubmit(t){const e=t.target,{submitter:o}=t;"dialog"===e.method&&o&&this.close(o.getAttribute("value")??this.returnValue)}handleCancel(t){if(t.target!==this.dialog)return;this.escapePressedWithoutCancel=!1;const e=!function(t,e){!e.bubbles||t.shadowRoot&&!e.composed||e.stopPropagation();const o=Reflect.construct(e.constructor,[e.type,e]),i=t.dispatchEvent(o);return i||e.preventDefault(),i}(this,t);t.preventDefault(),e||this.close()}handleClose(){var t;this.escapePressedWithoutCancel&&(this.escapePressedWithoutCancel=!1,null===(t=this.dialog)||void 0===t||t.dispatchEvent(new Event("cancel",{cancelable:!0})))}handleKeydown(t){"Escape"===t.key&&(this.escapePressedWithoutCancel=!0,setTimeout((()=>{this.escapePressedWithoutCancel=!1})))}async animateDialog(t){const{dialog:e,scrim:o,container:i,headline:a,content:n,actions:s}=this;if(!(e&&o&&i&&a&&n&&s))return;const{container:r,dialog:l,scrim:d,headline:c,content:h,actions:p}=t,v=[[e,l??[]],[o,d??[]],[i,r??[]],[a,c??[]],[n,h??[]],[s,p??[]]],m=[];for(const[t,e]of v)for(const o of e)m.push(t.animate(...o));await Promise.all(m.map((t=>t.finished)))}handleHeadlineChange(t){const e=t.target;this.hasHeadline=e.assignedElements().length>0}handleActionsChange(t){const e=t.target;this.hasActions=e.assignedElements().length>0}handleIconChange(t){const e=t.target;this.hasIcon=e.assignedElements().length>0}handleAnchorIntersection(t){const{target:e,isIntersecting:o}=t;e===this.topAnchor&&(this.isAtScrollTop=o),e===this.bottomAnchor&&(this.isAtScrollBottom=o)}getIsConnectedPromise(){return new Promise((t=>{this.isConnectedPromiseResolve=t}))}}e(y),o([i({type:Boolean})],y.prototype,"open",null),o([i({attribute:!1})],y.prototype,"returnValue",void 0),o([i()],y.prototype,"type",void 0),o([a("dialog")],y.prototype,"dialog",void 0),o([a(".scrim")],y.prototype,"scrim",void 0),o([a(".container")],y.prototype,"container",void 0),o([a(".headline")],y.prototype,"headline",void 0),o([a(".content")],y.prototype,"content",void 0),o([a(".actions")],y.prototype,"actions",void 0),o([n()],y.prototype,"isAtScrollTop",void 0),o([n()],y.prototype,"isAtScrollBottom",void 0),o([a(".scroller")],y.prototype,"scroller",void 0),o([a(".top.anchor")],y.prototype,"topAnchor",void 0),o([a(".bottom.anchor")],y.prototype,"bottomAnchor",void 0),o([n()],y.prototype,"hasHeadline",void 0),o([n()],y.prototype,"hasActions",void 0),o([n()],y.prototype,"hasIcon",void 0);const x=c`:host{border-start-start-radius:var(--md-dialog-container-shape-start-start, var(--md-dialog-container-shape, 28px));border-start-end-radius:var(--md-dialog-container-shape-start-end, var(--md-dialog-container-shape, 28px));border-end-end-radius:var(--md-dialog-container-shape-end-end, var(--md-dialog-container-shape, 28px));border-end-start-radius:var(--md-dialog-container-shape-end-start, var(--md-dialog-container-shape, 28px));display:contents;margin:auto;max-height:min(560px,100% - 48px);max-width:min(560px,100% - 48px);min-height:140px;min-width:280px;position:fixed;height:fit-content;width:fit-content}dialog{background:rgba(0,0,0,0);border:none;border-radius:inherit;flex-direction:column;height:inherit;margin:inherit;max-height:inherit;max-width:inherit;min-height:inherit;min-width:inherit;outline:none;overflow:visible;padding:0;width:inherit}dialog[open]{display:flex}::backdrop{background:none}.scrim{background:var(--md-sys-color-scrim, #000);display:none;inset:0;opacity:32%;pointer-events:none;position:fixed;z-index:1}:host([open]) .scrim{display:flex}h2{all:unset;align-self:stretch}.headline{align-items:center;color:var(--md-dialog-headline-color, var(--md-sys-color-on-surface, #1d1b20));display:flex;flex-direction:column;font-family:var(--md-dialog-headline-font, var(--md-sys-typescale-headline-small-font, var(--md-ref-typeface-brand, Roboto)));font-size:var(--md-dialog-headline-size, var(--md-sys-typescale-headline-small-size, 1.5rem));line-height:var(--md-dialog-headline-line-height, var(--md-sys-typescale-headline-small-line-height, 2rem));font-weight:var(--md-dialog-headline-weight, var(--md-sys-typescale-headline-small-weight, var(--md-ref-typeface-weight-regular, 400)));position:relative}slot[name=headline]::slotted(*){align-items:center;align-self:stretch;box-sizing:border-box;display:flex;gap:8px;padding:24px 24px 0}.icon{display:flex}slot[name=icon]::slotted(*){color:var(--md-dialog-icon-color, var(--md-sys-color-secondary, #625b71));fill:currentColor;font-size:var(--md-dialog-icon-size, 24px);margin-top:24px;height:var(--md-dialog-icon-size, 24px);width:var(--md-dialog-icon-size, 24px)}.has-icon slot[name=headline]::slotted(*){justify-content:center;padding-top:16px}.scrollable slot[name=headline]::slotted(*){padding-bottom:16px}.scrollable.has-headline slot[name=content]::slotted(*){padding-top:8px}.container{border-radius:inherit;display:flex;flex-direction:column;flex-grow:1;overflow:hidden;position:relative;transform-origin:top}.container::before{background:var(--md-dialog-container-color, var(--md-sys-color-surface-container-high, #ece6f0));border-radius:inherit;content:"";inset:0;position:absolute}.scroller{display:flex;flex:1;flex-direction:column;overflow:hidden;z-index:1}.scrollable .scroller{overflow-y:scroll}.content{color:var(--md-dialog-supporting-text-color, var(--md-sys-color-on-surface-variant, #49454f));font-family:var(--md-dialog-supporting-text-font, var(--md-sys-typescale-body-medium-font, var(--md-ref-typeface-plain, Roboto)));font-size:var(--md-dialog-supporting-text-size, var(--md-sys-typescale-body-medium-size, 0.875rem));line-height:var(--md-dialog-supporting-text-line-height, var(--md-sys-typescale-body-medium-line-height, 1.25rem));font-weight:var(--md-dialog-supporting-text-weight, var(--md-sys-typescale-body-medium-weight, var(--md-ref-typeface-weight-regular, 400)));height:min-content;position:relative}slot[name=content]::slotted(*){box-sizing:border-box;padding:24px}.anchor{position:absolute}.top.anchor{top:0}.bottom.anchor{bottom:0}.actions{position:relative}slot[name=actions]::slotted(*){box-sizing:border-box;display:flex;gap:8px;justify-content:flex-end;padding:16px 24px 24px}.has-actions slot[name=content]::slotted(*){padding-bottom:8px}md-divider{display:none;position:absolute}.has-headline.show-top-divider .headline md-divider,.has-actions.show-bottom-divider .actions md-divider{display:flex}.headline md-divider{bottom:0}.actions md-divider{top:0}@media(forced-colors: active){dialog{outline:2px solid WindowText}}/*# sourceMappingURL=dialog-styles.css.map */
`;let f=class extends y{};f.styles=[x],f=o([h("md-dialog")],f);const _=c`:host{border-start-start-radius:var(--_container-shape-start-start);border-start-end-radius:var(--_container-shape-start-end);border-end-start-radius:var(--_container-shape-end-start);border-end-end-radius:var(--_container-shape-end-end);box-sizing:border-box;cursor:pointer;display:inline-flex;gap:8px;min-height:var(--_container-height);outline:none;padding-block:calc((var(--_container-height) - max(var(--_label-text-line-height),var(--_icon-size)))/2);padding-inline-start:var(--_leading-space);padding-inline-end:var(--_trailing-space);place-content:center;place-items:center;position:relative;font-family:var(--_label-text-font);font-size:var(--_label-text-size);line-height:var(--_label-text-line-height);font-weight:var(--_label-text-weight);text-overflow:ellipsis;text-wrap:nowrap;user-select:none;-webkit-tap-highlight-color:rgba(0,0,0,0);vertical-align:top;--md-ripple-hover-color: var(--_hover-state-layer-color);--md-ripple-pressed-color: var(--_pressed-state-layer-color);--md-ripple-hover-opacity: var(--_hover-state-layer-opacity);--md-ripple-pressed-opacity: var(--_pressed-state-layer-opacity)}md-focus-ring{--md-focus-ring-shape-start-start: var(--_container-shape-start-start);--md-focus-ring-shape-start-end: var(--_container-shape-start-end);--md-focus-ring-shape-end-end: var(--_container-shape-end-end);--md-focus-ring-shape-end-start: var(--_container-shape-end-start)}:host([disabled]){cursor:default;pointer-events:none}.button{border-radius:inherit;cursor:inherit;display:inline-flex;align-items:center;justify-content:center;border:none;outline:none;-webkit-appearance:none;vertical-align:middle;background:rgba(0,0,0,0);text-decoration:none;min-width:calc(64px - var(--_leading-space) - var(--_trailing-space));width:100%;z-index:0;height:100%;font:inherit;color:var(--_label-text-color);padding:0;gap:inherit}.button::-moz-focus-inner{padding:0;border:0}:host(:hover) .button{color:var(--_hover-label-text-color)}:host(:focus-within) .button{color:var(--_focus-label-text-color)}:host(:active) .button{color:var(--_pressed-label-text-color)}.background{background-color:var(--_container-color);border-radius:inherit;inset:0;position:absolute}.label{overflow:hidden}:is(.button,.label,.label slot),.label ::slotted(*){text-overflow:inherit}:host([disabled]) .label{color:var(--_disabled-label-text-color);opacity:var(--_disabled-label-text-opacity)}:host([disabled]) .background{background-color:var(--_disabled-container-color);opacity:var(--_disabled-container-opacity)}@media(forced-colors: active){.background{border:1px solid CanvasText}:host([disabled]){--_disabled-icon-color: GrayText;--_disabled-icon-opacity: 1;--_disabled-container-opacity: 1;--_disabled-label-text-color: GrayText;--_disabled-label-text-opacity: 1}}:host([has-icon]:not([trailing-icon])){padding-inline-start:var(--_with-leading-icon-leading-space);padding-inline-end:var(--_with-leading-icon-trailing-space)}:host([has-icon][trailing-icon]){padding-inline-start:var(--_with-trailing-icon-leading-space);padding-inline-end:var(--_with-trailing-icon-trailing-space)}::slotted([slot=icon]){display:inline-flex;position:relative;writing-mode:horizontal-tb;fill:currentColor;flex-shrink:0;color:var(--_icon-color);font-size:var(--_icon-size);inline-size:var(--_icon-size);block-size:var(--_icon-size)}:host(:hover) ::slotted([slot=icon]){color:var(--_hover-icon-color)}:host(:focus-within) ::slotted([slot=icon]){color:var(--_focus-icon-color)}:host(:active) ::slotted([slot=icon]){color:var(--_pressed-icon-color)}:host([disabled]) ::slotted([slot=icon]){color:var(--_disabled-icon-color);opacity:var(--_disabled-icon-opacity)}.touch{position:absolute;top:50%;height:48px;left:0;right:0;transform:translateY(-50%)}:host([touch-target=wrapper]){margin:max(0px,(48px - var(--_container-height))/2) 0}:host([touch-target=none]) .touch{display:none}/*# sourceMappingURL=shared-styles.css.map */
`;function w(t){return t.currentTarget===t.target&&(t.composedPath()[0]===t.target&&(!t.target.disabled&&!function(t){const e=C;e&&(t.preventDefault(),t.stopImmediatePropagation());return async function(){C=!0,await null,C=!1}(),e}(t)))}let C=!1;const E=g(s);class A extends E{get name(){return this.getAttribute("name")??""}set name(t){this.setAttribute("name",t)}get form(){return this[m].form}constructor(){super(),this.disabled=!1,this.href="",this.target="",this.trailingIcon=!1,this.hasIcon=!1,this.type="submit",this.value="",this.handleActivationClick=t=>{w(t)&&this.buttonElement&&(this.focus(),function(t){const e=new MouseEvent("click",{bubbles:!0});t.dispatchEvent(e)}(this.buttonElement))},this.addEventListener("click",this.handleActivationClick)}focus(){var t;null===(t=this.buttonElement)||void 0===t||t.focus()}blur(){var t;null===(t=this.buttonElement)||void 0===t||t.blur()}render(){var t;const e=this.disabled&&!this.href,o=this.href?this.renderLink():this.renderButton(),i=this.href?"link":"button";return r`
      ${null===(t=this.renderElevationOrOutline)||void 0===t?void 0:t.call(this)}
      <div class="background"></div>
      <md-focus-ring part="focus-ring" for=${i}></md-focus-ring>
      <md-ripple for=${i} ?disabled="${e}"></md-ripple>
      ${o}
    `}renderButton(){const{ariaLabel:t,ariaHasPopup:e,ariaExpanded:o}=this;return r`<button
      id="button"
      class="button"
      ?disabled=${this.disabled}
      aria-label="${t||d}"
      aria-haspopup="${e||d}"
      aria-expanded="${o||d}">
      ${this.renderContent()}
    </button>`}renderLink(){const{ariaLabel:t,ariaHasPopup:e,ariaExpanded:o}=this;return r`<a
      id="link"
      class="button"
      aria-label="${t||d}"
      aria-haspopup="${e||d}"
      aria-expanded="${o||d}"
      href=${this.href}
      target=${this.target||d}
      >${this.renderContent()}
    </a>`}renderContent(){const t=r`<slot
      name="icon"
      @slotchange="${this.handleSlotChange}"></slot>`;return r`
      <span class="touch"></span>
      ${this.trailingIcon?d:t}
      <span class="label"><slot></slot></span>
      ${this.trailingIcon?t:d}
    `}handleSlotChange(){this.hasIcon=this.assignedIcons.length>0}}e(A),p(A),A.formAssociated=!0,A.shadowRootOptions={mode:"open",delegatesFocus:!0},o([i({type:Boolean,reflect:!0})],A.prototype,"disabled",void 0),o([i()],A.prototype,"href",void 0),o([i()],A.prototype,"target",void 0),o([i({type:Boolean,attribute:"trailing-icon",reflect:!0})],A.prototype,"trailingIcon",void 0),o([i({type:Boolean,attribute:"has-icon",reflect:!0})],A.prototype,"hasIcon",void 0),o([i()],A.prototype,"type",void 0),o([i({reflect:!0})],A.prototype,"value",void 0),o([a(".button")],A.prototype,"buttonElement",void 0),o([v({slot:"icon",flatten:!0})],A.prototype,"assignedIcons",void 0);class $ extends A{}const k=c`:host{--_container-height: var(--md-text-button-container-height, 40px);--_container-shape: var(--md-text-button-container-shape, 9999px);--_disabled-label-text-color: var(--md-text-button-disabled-label-text-color, var(--md-sys-color-on-surface, #1d1b20));--_disabled-label-text-opacity: var(--md-text-button-disabled-label-text-opacity, 0.38);--_focus-label-text-color: var(--md-text-button-focus-label-text-color, var(--md-sys-color-primary, #6750a4));--_hover-label-text-color: var(--md-text-button-hover-label-text-color, var(--md-sys-color-primary, #6750a4));--_hover-state-layer-color: var(--md-text-button-hover-state-layer-color, var(--md-sys-color-primary, #6750a4));--_hover-state-layer-opacity: var(--md-text-button-hover-state-layer-opacity, 0.08);--_label-text-color: var(--md-text-button-label-text-color, var(--md-sys-color-primary, #6750a4));--_label-text-font: var(--md-text-button-label-text-font, var(--md-sys-typescale-label-large-font, var(--md-ref-typeface-plain, Roboto)));--_label-text-line-height: var(--md-text-button-label-text-line-height, var(--md-sys-typescale-label-large-line-height, 1.25rem));--_label-text-size: var(--md-text-button-label-text-size, var(--md-sys-typescale-label-large-size, 0.875rem));--_label-text-weight: var(--md-text-button-label-text-weight, var(--md-sys-typescale-label-large-weight, var(--md-ref-typeface-weight-medium, 500)));--_pressed-label-text-color: var(--md-text-button-pressed-label-text-color, var(--md-sys-color-primary, #6750a4));--_pressed-state-layer-color: var(--md-text-button-pressed-state-layer-color, var(--md-sys-color-primary, #6750a4));--_pressed-state-layer-opacity: var(--md-text-button-pressed-state-layer-opacity, 0.12);--_disabled-icon-color: var(--md-text-button-disabled-icon-color, var(--md-sys-color-on-surface, #1d1b20));--_disabled-icon-opacity: var(--md-text-button-disabled-icon-opacity, 0.38);--_focus-icon-color: var(--md-text-button-focus-icon-color, var(--md-sys-color-primary, #6750a4));--_hover-icon-color: var(--md-text-button-hover-icon-color, var(--md-sys-color-primary, #6750a4));--_icon-color: var(--md-text-button-icon-color, var(--md-sys-color-primary, #6750a4));--_icon-size: var(--md-text-button-icon-size, 18px);--_pressed-icon-color: var(--md-text-button-pressed-icon-color, var(--md-sys-color-primary, #6750a4));--_leading-space: var(--md-text-button-leading-space, 12px);--_trailing-space: var(--md-text-button-trailing-space, 12px);--_with-leading-icon-leading-space: var(--md-text-button-with-leading-icon-leading-space, 12px);--_with-leading-icon-trailing-space: var(--md-text-button-with-leading-icon-trailing-space, 16px);--_with-trailing-icon-leading-space: var(--md-text-button-with-trailing-icon-leading-space, 16px);--_with-trailing-icon-trailing-space: var(--md-text-button-with-trailing-icon-trailing-space, 12px);--_container-color: none;--_disabled-container-color: none;--_disabled-container-opacity: 0;--_container-shape-start-start: var( --md-text-button-container-shape-start-start, var(--_container-shape) );--_container-shape-start-end: var( --md-text-button-container-shape-start-end, var(--_container-shape) );--_container-shape-end-end: var( --md-text-button-container-shape-end-end, var(--_container-shape) );--_container-shape-end-start: var( --md-text-button-container-shape-end-start, var(--_container-shape) )}/*# sourceMappingURL=text-styles.css.map */
`;let z=class extends ${};z.styles=[_,k],z=o([h("md-text-button")],z);const I=t=>t.preventDefault();let P=class extends s{render(){const t=this.params;return r`
      <md-dialog open @cancel=${I} @close=${this._handleClose}>
        ${t.title?r`<div slot="headline">${t.title}</div>`:""}
        ${t.text?r`<div slot="content">${t.text}</div>`:""}
        <div slot="actions">
          ${"prompt"===this.type?r`
                <md-text-button @click=${()=>this._setResult(!1)}>
                  ${t.cancelText||"Cancel"}
                </md-text-button>
              `:""}
          <md-text-button @click=${()=>this._setResult(!0)}>
            ${t.confirmText||"OK"}
          </md-text-button>
        </div>
      </md-dialog>
    `}_setResult(t){this.dialogResult(t),this.shadowRoot.querySelector("md-dialog").close()}_handleClose(){this.parentElement.removeChild(this)}};o([i()],P.prototype,"params",void 0),o([i()],P.prototype,"dialogResult",void 0),o([i()],P.prototype,"type",void 0),P=o([h("dialox-box")],P);export{P as DialogBox};
