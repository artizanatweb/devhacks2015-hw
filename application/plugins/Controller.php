<?php

/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

abstract class Application_Plugins_Controller extends Zend_Controller_Action
{
	public function init() {
            $this->_helper->viewRenderer->SetNoRender(TRUE);
            $this->view->layout()->disableLayout();
            $this->getResponse()->setHeader('Content-Type', 'application/json');
	}

}