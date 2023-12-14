import './App.css';
import React, {useEffect, useState} from 'react';
import {Avatar, Button, Form, Input, Layout, message, Modal, Popover, Table, Tabs} from 'antd';
import {UserOutlined} from '@ant-design/icons';
import axios from 'axios';
import CryptoJS from 'crypto-js';

const BASE_URL = "http://127.0.0.1:8009";
const {TabPane} = Tabs;
const {Header, Content} = Layout;

const App: React.FC = () => {
    const [dataSource, setDataSource] = useState([]);
    const [points, setPoints] = useState(0);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [aesKey, setAesKey] = useState('');
    const [aesIv, setAesIv] = useState('');
    const [RequestJSESSIONID, setRequestJSESSIONID] = useState('');
    const [RequestSESSIONID, setRequestSESSIONID] = useState('');

    const getCookieValue = (name: string) => {
        const value = "; " + document.cookie;
        const parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop()?.split(";").shift();
        return null;
    }

    useEffect(() => {
        // 读取cookie
        const uidFromCookie = getCookieValue('uid');
        const passwordFromCookie = getCookieValue('password');

        if (uidFromCookie && passwordFromCookie) {
            setUsername(uidFromCookie);
            setPassword(passwordFromCookie);
        }
    }, [])

    useEffect(() => {
        if (username && password) {
            // 如果username和password存在且不为空，发送积分检查请求
            const fetchPoints = async () => {
                try {
                    
                    const encryptedPassword = encrypt(password);
                    const response = await axios.post(`${BASE_URL}/user/point`, {
                        username,
                        password: encryptedPassword
                    });
                    setPoints(response.data.points);
                } catch (error) {
                    console.error("获取分数失败:", error);
                }
            };

            fetchPoints();
        }
    }, [username, password]);

    const toggleModal = (isVisible: boolean | ((prevState: boolean) => boolean)) => {
        setIsModalVisible(isVisible);
    };

    const handleChange = (type: string, event: { target: { value: React.SetStateAction<string>; }; }) => {
        switch (type) {
            case 'username':
                setUsername(event.target.value);
                break;
            case 'password':
                setPassword(event.target.value);
                break;
            case 'JSESSIONID':
                setRequestJSESSIONID(event.target.value);
                break;
            case 'SESSIONID':
                setRequestSESSIONID(event.target.value);
                break;
            default:
                break;
        }
    };

    useEffect(() => {
        const fetchAESKeyAndIv = async () => {
            try {
                const response = await axios.get(`${BASE_URL}/aes`);
                console.log("获取的key iv", response.data);
                setAesKey(response.data.key);
                setAesIv(response.data.iv);
            } catch (error) {
                console.error("获取AES key和iv失败:", error);
            }
        };

        fetchAESKeyAndIv();
    }, []);

    const encrypt = (text: string) => {
        const encrypted = CryptoJS.AES.encrypt(text, CryptoJS.enc.Utf8.parse(aesKey), {
            iv: CryptoJS.enc.Utf8.parse(aesIv),
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        });
        return encrypted.toString();
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const encryptedPassword = encrypt(password);
                const response = await axios.post(`${BASE_URL}/list`, {
                    username,
                    password: encryptedPassword
                });
                setDataSource(response.data);
            } catch (error) {
                console.error("请求失败:", error);
            }
        };

        const fetchPoints = async () => {
            try {
                const encryptedPassword = encrypt(password);
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
            const encryptedPassword = encrypt(password);
            const response = await axios.post(`${BASE_URL}/user/add`, {
                username,
                password: encryptedPassword
            });
            if (response.data === true) {
                message.success('登录成功');
                // 保存username和password到cookie
                document.cookie = `uid=${username}; path=/`;
                document.cookie = `password=${password}; path=/`;
            } else {
                message.error('登录失败');
            }
        } catch (error) {
            console.error("登录错误:", error);
            message.error('登录失败');
        }
    };

    const handleUpdateHeaders = async () => {
        try {
            const encryptedPassword = encrypt(password);
            await axios.post(`${BASE_URL}/user/headers`, {
                username,
                password: encryptedPassword,
                JSESSIONID: RequestJSESSIONID,
                sessionid: RequestSESSIONID,
            });
            message.success('账户更新成功');
        } catch (error) {
            console.error("Error updating headers:", error);
            message.error('账户更新失败');
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
                    <Avatar icon={<UserOutlined/>} onClick={() => toggleModal(true)}/>
                </Popover>
            </Header>
            <Content>
                <Table className="centered-table" dataSource={dataSource} columns={columns}/>
            </Content>

            <Modal
                centered
                open={isModalVisible}
                onCancel={() => toggleModal(false)}
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
                                <Button type="primary" onClick={handleLoginSubmit}>登录</Button>
                            </Form.Item>
                        </Form>
                    </TabPane>
                    <TabPane tab="更新账户" key="2">
                        <Form layout="vertical">
                            <Form.Item label="用户名" name="username">
                                <Input placeholder="请输入用户名" onChange={(e) => handleChange('username', e)} />
                            </Form.Item>
                            <Form.Item label="密码" name="password">
                                <Input placeholder="请输入密码" onChange={(e) => handleChange('password', e)} />
                            </Form.Item>
                            <Form.Item label="requestJSESSIONID" name="JSESSIONID">
                                <Input placeholder="JSESSIONID" onChange={(e) => handleChange('JSESSIONID', e)} />
                            </Form.Item>
                            <Form.Item label="requestSESSIONID" name="SESSIONID">
                                <Input placeholder="SESSIONID" onChange={(e) => handleChange('SESSIONID', e)} />
                            </Form.Item>
                            <Form.Item>
                                <Button type="primary" onClick={() => handleUpdateHeaders()}>更新</Button>
                            </Form.Item>
                        </Form>
                    </TabPane>
                </Tabs>
            </Modal>
        </Layout>
    );
};

export default App;
