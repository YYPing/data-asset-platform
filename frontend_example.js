/**
 * 材料管理前端示例代码
 * 演示如何使用材料管理 API
 */

// ==================== 配置 ====================

const API_BASE_URL = 'http://localhost:8000/api/v1';
let authToken = localStorage.getItem('auth_token') || '';

// 设置认证令牌
function setAuthToken(token) {
  authToken = token;
  localStorage.setItem('auth_token', token);
}

// 通用请求函数
async function apiRequest(url, options = {}) {
  const headers = {
    'Authorization': `Bearer ${authToken}`,
    ...options.headers
  };

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '请求失败');
  }

  return response.json();
}

// ==================== 材料 CRUD ====================

/**
 * 获取材料列表
 */
async function getMaterials(params = {}) {
  const queryString = new URLSearchParams(params).toString();
  return apiRequest(`/materials?${queryString}`);
}

/**
 * 获取材料详情
 */
async function getMaterial(materialId) {
  return apiRequest(`/materials/${materialId}`);
}

/**
 * 创建材料记录
 */
async function createMaterial(data) {
  return apiRequest('/materials', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}

/**
 * 更新材料信息
 */
async function updateMaterial(materialId, data) {
  return apiRequest(`/materials/${materialId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
}

/**
 * 删除材料
 */
async function deleteMaterial(materialId, softDelete = true) {
  return apiRequest(`/materials/${materialId}?soft_delete=${softDelete}`, {
    method: 'DELETE'
  });
}

// ==================== 文件上传（分片上传）====================

/**
 * 分片上传大文件
 * @param {File} file - 文件对象
 * @param {Object} materialInfo - 材料信息
 * @param {Function} onProgress - 进度回调函数
 */
async function uploadLargeFile(file, materialInfo, onProgress) {
  try {
    // 1. 初始化上传
    const initResponse = await apiRequest('/materials/upload', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        asset_id: materialInfo.assetId,
        material_name: materialInfo.name,
        material_type: materialInfo.type,
        stage: materialInfo.stage,
        is_required: materialInfo.isRequired || false,
        file_name: file.name,
        file_size: file.size
      })
    });

    const { session_id, total_chunks, chunk_size } = initResponse;
    console.log(`上传会话创建成功: ${session_id}, 总分片数: ${total_chunks}`);

    // 2. 分片上传
    for (let i = 0; i < total_chunks; i++) {
      const start = i * chunk_size;
      const end = Math.min(start + chunk_size, file.size);
      const chunk = file.slice(start, end);

      const formData = new FormData();
      formData.append('chunk_index', i);
      formData.append('chunk_data', chunk);

      const chunkResponse = await fetch(
        `${API_BASE_URL}/materials/${session_id}/upload-chunk`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${authToken}` },
          body: formData
        }
      );

      if (!chunkResponse.ok) {
        throw new Error(`分片 ${i} 上传失败`);
      }

      const { progress } = await chunkResponse.json();
      
      // 调用进度回调
      if (onProgress) {
        onProgress(progress, i + 1, total_chunks);
      }

      console.log(`分片 ${i + 1}/${total_chunks} 上传成功，进度: ${progress.toFixed(2)}%`);
    }

    // 3. 完成上传
    const completeFormData = new FormData();
    completeFormData.append('material_name', materialInfo.name);
    completeFormData.append('material_type', materialInfo.type || '');
    completeFormData.append('stage', materialInfo.stage);
    completeFormData.append('is_required', materialInfo.isRequired || false);

    const completeResponse = await fetch(
      `${API_BASE_URL}/materials/${session_id}/complete-upload`,
      {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${authToken}` },
        body: completeFormData
      }
    );

    if (!completeResponse.ok) {
      throw new Error('完成上传失败');
    }

    const result = await completeResponse.json();
    console.log('上传完成！', result);

    return result;

  } catch (error) {
    console.error('上传失败:', error);
    throw error;
  }
}

/**
 * 取消上传
 */
async function cancelUpload(sessionId) {
  return apiRequest(`/materials/${sessionId}/cancel-upload`, {
    method: 'DELETE'
  });
}

// ==================== 文件下载 ====================

/**
 * 下载材料文件
 */
async function downloadMaterial(materialId) {
  const response = await apiRequest(`/materials/${materialId}/download`);
  const { download_url } = response;
  
  // 在新窗口打开下载链接
  window.open(download_url, '_blank');
  
  return response;
}

// ==================== 哈希验证 ====================

/**
 * 获取材料哈希
 */
async function getMaterialHash(materialId, algorithm = 'sha256') {
  return apiRequest(`/materials/${materialId}/hash?algorithm=${algorithm}`);
}

/**
 * 验证材料完整性
 */
async function verifyMaterial(materialId, expectedHash, algorithm = 'sha256') {
  return apiRequest(`/materials/${materialId}/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ expected_hash: expectedHash, algorithm })
  });
}

// ==================== 版本管理 ====================

/**
 * 创建新版本
 */
async function createVersion(materialId, versionData) {
  return apiRequest(`/materials/${materialId}/versions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(versionData)
  });
}

/**
 * 获取版本历史
 */
async function getVersionHistory(materialId) {
  return apiRequest(`/materials/${materialId}/versions`);
}

// ==================== 审核流程 ====================

/**
 * 提交审核
 */
async function submitForReview(materialId, comment) {
  return apiRequest(`/materials/${materialId}/submit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comment })
  });
}

/**
 * 审核通过
 */
async function approveMaterial(materialId, comment) {
  return apiRequest(`/materials/${materialId}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comment })
  });
}

/**
 * 审核驳回
 */
async function rejectMaterial(materialId, comment) {
  return apiRequest(`/materials/${materialId}/reject`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ comment })
  });
}

// ==================== UI 组件示例 ====================

/**
 * 文件上传组件
 */
class FileUploader {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.file = null;
    this.sessionId = null;
    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="file-uploader">
        <input type="file" id="fileInput" />
        <div class="progress-container" style="display: none;">
          <div class="progress-bar">
            <div class="progress-fill" style="width: 0%"></div>
          </div>
          <div class="progress-text">0%</div>
        </div>
        <button id="uploadBtn" disabled>上传</button>
        <button id="cancelBtn" style="display: none;">取消</button>
      </div>
    `;

    this.fileInput = this.container.querySelector('#fileInput');
    this.uploadBtn = this.container.querySelector('#uploadBtn');
    this.cancelBtn = this.container.querySelector('#cancelBtn');
    this.progressContainer = this.container.querySelector('.progress-container');
    this.progressFill = this.container.querySelector('.progress-fill');
    this.progressText = this.container.querySelector('.progress-text');

    this.fileInput.addEventListener('change', (e) => this.onFileSelect(e));
    this.uploadBtn.addEventListener('click', () => this.upload());
    this.cancelBtn.addEventListener('click', () => this.cancel());
  }

  onFileSelect(e) {
    this.file = e.target.files[0];
    this.uploadBtn.disabled = !this.file;
  }

  async upload() {
    if (!this.file) return;

    this.uploadBtn.disabled = true;
    this.cancelBtn.style.display = 'inline-block';
    this.progressContainer.style.display = 'block';

    try {
      const result = await uploadLargeFile(
        this.file,
        {
          assetId: 1,
          name: this.file.name,
          type: '文档',
          stage: 'registration',
          isRequired: true
        },
        (progress, current, total) => {
          this.updateProgress(progress);
          console.log(`上传进度: ${current}/${total} (${progress.toFixed(2)}%)`);
        }
      );

      alert(`上传成功！材料ID: ${result.material_id}`);
      this.reset();

    } catch (error) {
      alert(`上传失败: ${error.message}`);
      this.uploadBtn.disabled = false;
    }
  }

  async cancel() {
    if (this.sessionId) {
      try {
        await cancelUpload(this.sessionId);
        alert('上传已取消');
      } catch (error) {
        console.error('取消上传失败:', error);
      }
    }
    this.reset();
  }

  updateProgress(progress) {
    this.progressFill.style.width = `${progress}%`;
    this.progressText.textContent = `${progress.toFixed(2)}%`;
  }

  reset() {
    this.file = null;
    this.sessionId = null;
    this.fileInput.value = '';
    this.uploadBtn.disabled = true;
    this.cancelBtn.style.display = 'none';
    this.progressContainer.style.display = 'none';
    this.progressFill.style.width = '0%';
    this.progressText.textContent = '0%';
  }
}

/**
 * 材料列表组件
 */
class MaterialList {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.materials = [];
    this.currentPage = 1;
    this.pageSize = 20;
    this.init();
  }

  async init() {
    await this.loadMaterials();
    this.render();
  }

  async loadMaterials() {
    try {
      const response = await getMaterials({
        page: this.currentPage,
        page_size: this.pageSize,
        asset_id: 1
      });
      this.materials = response.items;
      this.total = response.total;
    } catch (error) {
      console.error('加载材料列表失败:', error);
    }
  }

  render() {
    const html = `
      <div class="material-list">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>材料名称</th>
              <th>类型</th>
              <th>阶段</th>
              <th>状态</th>
              <th>上传时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            ${this.materials.map(m => `
              <tr>
                <td>${m.id}</td>
                <td>${m.material_name}</td>
                <td>${m.material_type || '-'}</td>
                <td>${m.stage}</td>
                <td>${m.status}</td>
                <td>${new Date(m.uploaded_at).toLocaleString()}</td>
                <td>
                  <button onclick="downloadMaterial(${m.id})">下载</button>
                  <button onclick="viewVersions(${m.id})">版本</button>
                  <button onclick="deleteMaterial(${m.id})">删除</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <div class="pagination">
          <button onclick="materialList.prevPage()" ${this.currentPage === 1 ? 'disabled' : ''}>上一页</button>
          <span>第 ${this.currentPage} 页，共 ${Math.ceil(this.total / this.pageSize)} 页</span>
          <button onclick="materialList.nextPage()" ${this.currentPage * this.pageSize >= this.total ? 'disabled' : ''}>下一页</button>
        </div>
      </div>
    `;
    this.container.innerHTML = html;
  }

  async prevPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      await this.loadMaterials();
      this.render();
    }
  }

  async nextPage() {
    if (this.currentPage * this.pageSize < this.total) {
      this.currentPage++;
      await this.loadMaterials();
      this.render();
    }
  }
}

// ==================== 使用示例 ====================

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
  // 设置认证令牌
  setAuthToken('YOUR_JWT_TOKEN');

  // 初始化文件上传组件
  const uploader = new FileUploader('uploaderContainer');

  // 初始化材料列表组件
  const materialList = new MaterialList('materialListContainer');

  // 全局暴露，方便调试
  window.uploader = uploader;
  window.materialList = materialList;
});

// 导出所有函数
export {
  setAuthToken,
  getMaterials,
  getMaterial,
  createMaterial,
  updateMaterial,
  deleteMaterial,
  uploadLargeFile,
  cancelUpload,
  downloadMaterial,
  getMaterialHash,
  verifyMaterial,
  createVersion,
  getVersionHistory,
  submitForReview,
  approveMaterial,
  rejectMaterial,
  FileUploader,
  MaterialList
};
