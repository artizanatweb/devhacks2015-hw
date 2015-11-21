<?php

class DeviceController extends Application_Plugins_Controller
{

    public function init()
    {
        /* Initialize action controller here */
        parent::init();
    }

    public function indexAction()
    {
        // action body
        $turn = $this->getParam('turn', NULL);
        
    }


}

