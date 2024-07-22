import { createMiddleware } from "@mswjs/http-middleware";
import cors from "cors";
import express from "express";
import { handlers } from "./handlers";

const app = express();

app.use(cors());
app.use(express.json());
app.use(createMiddleware(...handlers));

app.listen(9090);
