import { useState } from "react";
import { api } from "../api";
import { Link, useNavigate } from "react-router-dom";

export default function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit() {
    setErr("");
    setLoading(true);
    try {
      const r = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("token", r.access_token);
      nav("/", { replace: true });
    } catch (e: any) {
      setErr("登录失败：邮箱或密码不正确，或后端未启动（8000）。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <div className="card">
        <div className="brand">CiteCheck</div>
        <div className="title">登录</div>
        <p className="subtitle">登录后即可管理文献、DOI 补全与生成 GB/T 7714。</p>

        <div className="field">
          <label>邮箱</label>
          <input
            placeholder="name@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="field">
          <label>密码</label>
          <input
            placeholder="••••••••"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => (e.key === "Enter" ? onSubmit() : null)}
          />
        </div>

        <button className="button" disabled={loading} onClick={onSubmit}>
          {loading ? "登录中..." : "登录"}
        </button>

        {err ? <div className="error">{err}</div> : null}

        <div className="row">
          <span>还没有账号？</span>
          <Link to="/register">去注册 →</Link>
        </div>
      </div>
    </div>
  );
}