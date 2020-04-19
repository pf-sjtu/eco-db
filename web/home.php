<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width,height=device-height,inital-scale=1.0,maximum-scale=2.0,user-scalable=no" />
    <title>SURFES</title>
    <link rel="shortcut icon" href="pic/icon2.64.ico" />
    <link rel="stylesheet" type="text/css" href="css/indexLayout.css" />
</head>

<body>
    <?php
    session_start();
    if (!isset($_SESSION['username'])) {
        header("location:index.php");
        exit;
    }
    ?>
    <!-- 加载外部资源 -->
    <div id="loadingProgress">
        <div id="loadingProgressBox">
            <div id="loadingPageIcon">
                <img src="pic/icon2.small.png" alt="" /><br />
                <p class="name">上海城市森林生态站数据库系统</p>
                <p class="enName">
                    S<span>hanghai</span> UR<span>ban</span> F<span>orest</span> E<span>cosystem research</span> S<span>tation</span> <span>database</span>
                </p>
            </div>
            <br /><br />
            <span class="loadingItem">正在加载资源</span><br />
            <progress id="loadingProgressBar" value="0" max="6"></progress>
        </div>
        <!-- Step1 vue -->
        <script>
            console.log('Loading Vue...')
        </script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/vue@2.6.11/dist/vue.min.js"></script>
        <!-- <script type="text/javascript" src="ext/vue/vue.js"></script> -->
        <script type="text/javascript" src="js/loadingStep.js"></script>
        <!-- Step2 iveiw -->
        <script>
            console.log('Loading iVeiw...')
            loadingForward()
        </script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/view-design@4.1.3/dist/iview.min.js"></script>
        <!-- <script type="text/javascript" src="ext/viewui/iview.min.js"></script> -->
        <!-- Step3 ECharts -->
        <script>
            console.log('Loading ECharts...')
            loadingForward()
        </script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@4.7.0/dist/echarts.min.js"></script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/echarts@4.7.0/map/js/province/shanghai.js"></script>
        <!-- <script type="text/javascript" src="ext/echarts/echarts2.js"></script> -->
        <!-- Step4 JQuery -->
        <script>
            console.log('Loading JQuery...')
            loadingForward()
        </script>
        <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/jquery@3.4.1/dist/jquery.min.js"></script>
        <!-- <script type="text/javascript" src="ext/jquery/jquery-3.4.1.js"></script> -->
        <!-- Step5 myScripts -->
        <script>
            console.log('Loading Customized Scripts and CSS...')
            loadingForward()
        </script>
        <script type="text/javascript" src="js/pfUtils.js"></script>
        <?php require_once("account/qureyAuth.php") ?>
        <script type="text/javascript" src="js/layout.js"></script>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/view-design@4.1.3/dist/styles/iview.css" />
        <!-- <link rel="stylesheet" type="text/css" href="ext/viewui/iview.css"> -->
        <link rel="stylesheet" type="text/css" href="css/indexDetail.css" />
        <!-- Step6 deploy -->
        <script>
            console.log('Deploying...')
            loadingForward()
        </script>
    </div>
    <div id="topNav">
        <template v-if="isPC()">
            <link rel="stylesheet" type="text/css" href="css/pc.css" />
        </template>
        <template v-else="!isPC()">
            <link rel="stylesheet" type="text/css" href="css/phone.css" />
        </template>
        <Row>
            <div id="headingName">
                <template v-if="!isPC()">
                    <button @click="menuOpen=true" id="menuButton">
                        <Icon type="ios-menu"></Icon>
                    </button>
                    <Drawer title="菜单" :closable="false" :width="menuWidth" v-model="menuOpen" placement="left">
                        <i-menu @on-select="updateHiddenState" mode="vertical" :theme="theme" :active-name="activeName">
                            <menu-item v-for="(item, index) in items" :key="index" :name="index">
                                <icon :type="item.iconType"></icon>
                                {{ item.title }}
                            </menu-item>
                            <br />
                        </i-menu>
                    </Drawer>
                </template>
                <div id="title">
                    <img class="icon" src="pic/icon2.dark.small.png" alt="" />
                    SURFES<span>上海城市森林生态站数据库系统</span>
                </div>
            </div>
        </Row>
        <Row v-if="isPC()">
            <div id="topMenu">
                <i-menu @on-select="updateHiddenState" mode="horizontal" :theme="theme" :active-name="activeName">
                    <menu-item v-for="(item, index) in items" :key="index" :name="index">
                        <icon :type="item.iconType"></icon>
                        {{ item.title }}
                    </menu-item>
                </i-menu>
            </div>
        </Row>
    </div>

    <div id="container">
        <div id="heading"></div>
        <div id="content">
            <div id="contentBody">
                <div id="live" hidden></div>
                <div id="historyGraph" hidden></div>
                <div id="historyTable" hidden></div>
                <div id="download" hidden></div>
                <div id="setting" hidden></div>
                <div id="account" hidden></div>
                <div id="about" hidden></div>
            </div>
        </div>
        <div id="footing">
            <div id="footingInfo"></div>
        </div>
    </div>
    <script type="text/javascript" src="js/index.js"></script>
    <div id="afterLoad" hidden></div>
</body>

</html>