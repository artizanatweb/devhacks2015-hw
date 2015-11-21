<?php

class Application_Model_ZMQClient
{
    protected $socket;
    protected $address;
    protected $port;
    protected $message;

    public function __construct() {
        $config = Zend_Registry::get('config');
        $this->address = $config->zmq->address;
        $this->port = $config->zmq->port;
        
        $this->message = array(
            'type' => '',
        );
    }
    
    public function open()
    {
        $context = new ZMQContext();
        $this->socket = new ZMQSocket($context, ZMQ::SOCKET_REQ);
        $this->socket->connect($this->address.":".  $this->port);
    }
    
    public function send(array $arrMessage)
    {
        $message = json_encode($arrMessage);
        $this->socket->send($message);
        return $this->socket->recv();
    }
    
    public function close()
    {
        $this->socket->close();
    }
    
    public function status()
    {
        $this->message['type'] = 'status';
        $message = json_encode($this->message);
        $this->socket->send($message);
        return $this->socket->recv();
    }
}

