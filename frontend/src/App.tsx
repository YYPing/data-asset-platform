import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import AppLayout from './components/AppLayout';
import Login from './pages/auth/Login';
import AssetList from './pages/asset/AssetList';
import AssetDetail from './pages/asset/AssetDetail';
import AssetCreate from './pages/asset/AssetCreate';
import ApprovalList from './pages/approval/ApprovalList';
import AssessmentList from './pages/assess/AssessmentList';
import AdminPanel from './pages/admin/AdminPanel';
import HolderDashboard from './pages/dashboard/HolderDashboard';
import CityDashboard from './pages/monitor/CityDashboard';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  return token ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<PrivateRoute><AppLayout /></PrivateRoute>}>
            <Route index element={<Navigate to="/assets" />} />
            <Route path="assets" element={<AssetList />} />
            <Route path="assets/create" element={<AssetCreate />} />
            <Route path="assets/:id" element={<AssetDetail />} />
            <Route path="approval" element={<ApprovalList />} />
            <Route path="assess" element={<AssessmentList />} />
            <Route path="admin" element={<AdminPanel />} />
            <Route path="dashboard" element={<HolderDashboard />} />
            <Route path="monitor" element={<CityDashboard />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
