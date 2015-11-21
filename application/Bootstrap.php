<?php

class Bootstrap extends Zend_Application_Bootstrap_Bootstrap
{

    protected function _initPlugins()
    {
        require_once APPLICATION_PATH.'/plugins/Controller.php';
        $front = Zend_Controller_Front::getInstance(); 
        return $front;
    }

    protected function _initConfigs()
    {
        $config = new Zend_Config_Ini(APPLICATION_PATH.'/configs/application.ini', 'production');
        Zend_Registry::set('config', $config);
    }
}

