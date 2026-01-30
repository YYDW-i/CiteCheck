import { useState } from "react";
import { api } from "../api";
import { Link, useNavigate } from "react-router-dom";

export default function Register() {
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit() {
    setErr("");
    if (!email.includes("@")) return setErr("请输入正确的邮箱。");
    if (password.length < 6) return setErr("密码至少 6 位。");
    if (password !== password2) return setErr("两次输入的密码不一致。");
    
    const bytes = new TextEncoder().encode(password).length;
    console.log("password chars =", password.length, "password bytes =", bytes);
    console.log("password raw =", JSON.stringify(password));

    setLoading(true);
    try {
      await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      nav("/login");
    } catch (e: any) {
      const msg = String(e?.message || e);
      if (msg.includes("409") || msg.includes("already registered")) {
        setErr("注册失败：该邮箱已注册，请直接去登录。");
      } else if (msg.includes("500")) {
        setErr("注册失败：服务器内部错误（后端注册逻辑异常）。");
      } else {
        setErr("注册失败：" + msg);
      }
    }finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <div className="card">
        <div className="brand">CiteCheck</div>
        <div className="title">注册</div>
        <p className="subtitle">创建账号后，你的文献库会保存在后端数据库中。</p>

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
            placeholder="至少 6 位"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <div className="field">
          <label>确认密码</label>
          <input
            placeholder="再输入一遍"
            type="password"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
            onKeyDown={(e) => (e.key === "Enter" ? onSubmit() : null)}
          />
        </div>

        <button className="button" disabled={loading} onClick={onSubmit}>
          {loading ? "注册中..." : "注册"}
        </button>

        {err ? <div className="error">{err}</div> : null}

        <div className="row">
          <span>已有账号？</span>
          <Link to="/login">去登录 →</Link>
        </div>
      </div>
    </div>
  );
}