<?php

class StatusController extends Application_Plugins_Controller
{

    public function init()
    {
        /* Initialize action controller here */
        parent::init();
    }

    public function indexAction()
    {
        $message = array(
            'type' => '',
            'device' => '',
        );
        $response = json_encode(array());
        // action body
        $zmqClient = new Application_Model_ZMQClient();
        $zmqClient->open();
        
        $turn = $this->getParam('turn', NULL);
        $device = $this->getParam('device','a');
        $message['device'] = $device;
        
        switch ($turn) {
            case 'red':
                // set red
                $message['type'] = 'color';
                $message['color'] = 'red';
                $status = $zmqClient->send($message);
                // return the state
                $response = $status;
                break;
            
            case 'yellow':
                // set yellow
                $message['type'] = 'color';
                $message['color'] = 'yellow';
                $status = $zmqClient->send($message);
                // return the state
                $response = $status;
                break;
            
            case 'green':
                // set green
                $message['type'] = 'color';
                $message['color'] = 'green';
                $status = $zmqClient->send($message);
                // return the state
                $response = $status;
                break;

            default:
                // get the state
                $status = $zmqClient->status();
                // return the state
                $response = $status;
                break;
        }
        
        $zmqClient->close();
        echo $response;
        return;
    }
}

