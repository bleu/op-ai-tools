import { createMiddleware } from "@mswjs/http-middleware";
import express from "express";
import cors from "cors";
import { handlers } from "./handlers";

const app = express();

app.use(cors());
app.use(express.json());
app.use(createMiddleware(...handlers));

app.listen(9090);
