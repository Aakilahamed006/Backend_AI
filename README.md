🚀 AI-Powered Natural Language to SQL Backend

A secure, AI-driven backend system that converts natural language into SQL queries, validates them using a vector memory system, and executes them safely with JWT authentication and role-based access control.

🧠 Overview

This system allows users to query databases using natural language. It uses AI to generate SQL, stores successful queries in a vector database for reuse, and enforces strict security rules before execution.

It supports:

Development mode (training + storing queries)
Live mode (secure execution only)
JWT authentication
Role-based access control
Query permission rules
Safe SQL execution

<img width="1408" height="768" alt="architecture (2)" src="https://github.com/user-attachments/assets/929b212a-f077-4367-838b-917dda9d1bcd" />



📦 Features
🧠 Natural language → SQL conversion
📚 Vector memory for query reuse
🔐 JWT authentication
👮 Role-based access control (RBAC)
🚫 Block DELETE / UPDATE operations
🧪 Dev mode for training queries
🚀 Live mode for production-safe execution
🗄️ Multi-database support (SQLite, PostgreSQL, MySQL)



🔐 Authentication System
🔑 JWT Login Flow
User logs in
Backend validates credentials
Returns JWT token
Token contains user role


<img width="662" height="494" alt="image" src="https://github.com/user-attachments/assets/3097d8f9-2f36-4f6f-afae-ada8b8bb91fe" />


3. Operation Restrictions
allow_delete = false → DELETE blocked
allow_update = false → UPDATE blocked
4. AI Safety Layer
AI-generated SQL is validated before execution
Dangerous queries are blocked
🗄️ Database Support

Supports:

SQLite (default)
PostgreSQL
MySQL

Configured via .env



