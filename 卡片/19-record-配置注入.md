```
@ConfigurationProperties(prefix = "swu")
public record SwuProperties(
        String key,
        String UA,
        String defaultAvatarUrl,
        Waf waf,
        Email email,
        Miniapp miniapp,
        Jw jw
) {
    public record Waf(String ip) {}
    public record Email(String alias) {}
    public record Miniapp(String appid, String appsecret) {}
    public record Jw(String xnm, String xqm, String xnmmc, String xqmmc) {}
}
```