import { env } from "../../env";
import { z } from "zod";
import axios from "axios";

const serverStatusEnum = z.enum(['online', 'starting up', "shutting down", 'offline', 'error'] as const);
const serverInfoSchema = z.object({
    status: serverStatusEnum,
    numPlayers: z.coerce.number(),
    maxPlayers: z.coerce.number(),
    motd: z.string(),
    version: z.string(),
    players: z.array(z.string()),
    logs: z.array(z.string()),
});

const instanceStateEnum = z.enum(['pending', 'running', 'shutting-down', 'terminated', 'stopping', 'stopped', 'error'] as const);
const instanceInfoSchema = z.object({
    instanceStatus: instanceStateEnum,
    instanceIP: z.nullable(z.string()),
    serverInfo: z.nullable(serverInfoSchema),
});
type InstanceInfo = z.infer<typeof instanceInfoSchema>;

const instanceStateTransitionSchema = z.object({
    currentState: instanceStateEnum,
    previousState: instanceStateEnum,
})
type InstanceStateTransition = z.infer<typeof instanceStateTransitionSchema>;

const api = axios.create({
    baseURL: env.NEXT_PUBLIC_API_URL,
    responseType: "json",
    withCredentials: false,
});

export async function getInstanceInfo(): Promise<InstanceInfo> {
    // Fetch the server info from the API
    try {
        const response = await api.get("/instance_info");
        console.log(response.data)
        return instanceInfoSchema.parse(response.data)
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error(error.toJSON());
        }
        console.error(error);

        return instanceInfoSchema.parse({ instanceStatus: "error", instanceIP: null, serverInfo: null });
    }
}

export async function startInstance(): Promise<InstanceStateTransition> {
    try {
        const response = await api.post("/start_instance");
        console.log(response.data)
        return instanceStateTransitionSchema.parse(response.data)
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error(error.toJSON());
        } else {
            console.error(error);
        }
        return instanceStateTransitionSchema.parse({ currentState: "error", previousState: "error" })
    }
}

export async function stopInstance(): Promise<string> {
    try {
        const response = await api.post("/stop_instance");
        console.log(response.data)
        return String(response.data)
    } catch (error) {
        if (axios.isAxiosError(error)) {
            console.error(error.toJSON());
        } else {
            console.error(error);
        }
        return "error"
    }
}
