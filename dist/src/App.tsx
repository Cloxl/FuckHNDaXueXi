import './App.css';
import React, {useEffect, useState} from 'react';
import {Avatar, Button, Form, Input, Layout, message, Modal, Popover, Table, Tabs} from 'antd';
import {UserOutlined} from '@ant-design/icons';
import axios from 'axios';
import CryptoJS from 'crypto-js';

const BASE_URL = "http://127.0.0.1:11220";
const {TabPane} = Tabs;
const {Header, Content} = Layout;

const App: React.FC = () => {
    const [dataSource, setDataSource] = useState([]);
    const [points, setPoints] = useState(0);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [requestHeader, setRequestHeader] = useState('');

    const showModal = () => {
        setIsModalVisible(true);
    };

    const handleCancel = () => {
        setIsModalVisible(false);
    };

    const getAESKeyAndIv = async () => {
        const response = await axios.get(`${BASE_URL}/aes`);
        return response.data;
    };

    const encrypt = (text: string, key: any, iv: any) => {
        const encrypted = CryptoJS.AES.encrypt(text, CryptoJS.enc.Utf8.parse(key), {
            iv: CryptoJS.enc.Utf8.parse(iv),
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        });
        return encrypted.toString();
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const {key, iv} = await getAESKeyAndIv();
                const encryptedPassword = encrypt(password, key, iv);
                const response = await axios.post(`${BASE_URL}/list`, {
                    username,
                    password: encryptedPassword
                });
                setDataSource(response.data);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        const fetchPoints = async () => {
            try {
                const {key, iv} = await getAESKeyAndIv();
                const encryptedPassword = encrypt(password, key, iv);
                const response = await axios.post(`${BASE_URL}/user/point`, {
                    username,
                    password: encryptedPassword
                });
                setPoints(response.data.points);
            } catch (error) {
                console.error("Error fetching points:", error);
            }
        };

        fetchData();
        fetchPoints();
    }, [username, password]);

    const handleLoginSubmit = async () => {
        try {
            const {key, iv} = await getAESKeyAndIv();
            const encryptedPassword = encrypt(password, key, iv);
            const response = await axios.post(`${BASE_URL}/user/add`, {
                username,
                password: encryptedPassword
            });
            if (response.data === true) {
                message.success('登录成功');
                // Save cookie logic here
                document.cookie = "loggedIn=true";
            } else {
                message.error('登录失败');
            }
        } catch (error) {
            console.error("Error during login:", error);
            message.error('登录失败');
        }
    };

    const handleUpdateHeaders = async (requestHeader: string) => {
        try {
            const {key, iv} = await getAESKeyAndIv();
            const encryptedPassword = encrypt(password, key, iv);
            const encodedRequestHeader = CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse(requestHeader));
            await axios.post(`${BASE_URL}/user/headers`, {
                username,
                password: encryptedPassword,
                requestHeader: encodedRequestHeader
            });
            message.success('请求头更新成功');
        } catch (error) {
            console.error("Error updating headers:", error);
            message.error('请求头更新失败');
        }
    };

    const columns = [
        {
            title: '类型',
            dataIndex: 'type',
            key: 'type',
        },
        {
            title: 'ID',
            dataIndex: 'id',
            key: 'id',
        },
        {
            title: '标题',
            dataIndex: 'title',
            key: 'title',
        },
        {
            title: '增加的积分',
            dataIndex: 'points',
            key: 'points',
        },
    ];

    return (
        <Layout>
            <Header style={{display: 'flex', alignItems: 'center', justifyContent: 'flex-end'}}>
                <Popover content="这里好像是你的积分?" trigger="hover">
                    <span style={{marginRight: '10px', color: 'black'}}>积分: {points}</span>
                </Popover>
                <Popover content="什么?这里居然是用户中心?" trigger="hover">
                    <Avatar icon={<UserOutlined/>} onClick={showModal}/>
                </Popover>
            </Header>
            <Content>
                <Table className="centered-table" dataSource={dataSource} columns={columns}/>
            </Content>

            <Modal
                centered
                visible={isModalVisible}
                onCancel={handleCancel}
                footer={null}
                style={{maxWidth: '500px', maxHeight: '300px', marginTop: 'calc(50vh - 150px)'}}
            >
                <Tabs defaultActiveKey="1">
                    <TabPane tab="用户中心" key="1">
                        <Form layout="vertical">
                            <Form.Item label="用户名" name="username">
                                <Input placeholder="请输入用户名"/>
                            </Form.Item>
                            <Form.Item label="密码" name="password">
                                <Input.Password placeholder="请输入密码"/>
                            </Form.Item>
                            <Form.Item>
                                <Button type="primary" onClick={handleLoginSubmit}>提交</Button>
                            </Form.Item>
                        </Form>
                    </TabPane>
                    <TabPane tab="更新请求头" key="2">
                        <Form layout="vertical">
                            <Form.Item label="用户名" name="username">
                                <Input placeholder="请输入用户名"/>
                            </Form.Item>
                            <Form.Item label="密码" name="password">
                                <Input placeholder="请输入密码"/>
                            </Form.Item>
                            <Form.Item label="请求头" name="requestHeader">
                                <Input placeholder="请输入请求头"/>
                            </Form.Item>
                            <Form.Item>
                                <Button type="primary" onClick={() => handleUpdateHeaders(requestHeader)}>更新</Button>
                            </Form.Item>
                        </Form>
                    </TabPane>
                </Tabs>
            </Modal>
        </Layout>
    );
};

export default App;
